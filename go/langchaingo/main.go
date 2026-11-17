// Command langchaingo serves an order-status agent built with LangChainGo.
//
// POST /run {"prompt": "What's the status of order 42?"} -> {"answer": "..."}
// Needs OPENAI_API_KEY. Run: go run .
package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/tmc/langchaingo/llms"
	"github.com/tmc/langchaingo/llms/openai"
)

const (
	system   = "You are a customer support agent. Use your tools to answer questions about orders."
	maxSteps = 8
)

var tools = []llms.Tool{{
	Type: "function",
	Function: &llms.FunctionDefinition{
		Name:        "get_order_status",
		Description: "Look up the shipping status of an order by its id.",
		Parameters: map[string]any{
			"type":       "object",
			"properties": map[string]any{"order_id": map[string]any{"type": "string"}},
			"required":   []string{"order_id"},
		},
	},
}}

func getOrderStatus(orderID string) string {
	return fmt.Sprintf("Order %s: shipped, arriving Friday.", orderID)
}

func ask(ctx context.Context, llm llms.Model, prompt string) (string, error) {
	messages := []llms.MessageContent{
		llms.TextParts(llms.ChatMessageTypeSystem, system),
		llms.TextParts(llms.ChatMessageTypeHuman, prompt),
	}
	for range maxSteps {
		resp, err := llm.GenerateContent(ctx, messages, llms.WithTools(tools))
		if err != nil {
			return "", fmt.Errorf("generate: %w", err)
		}
		choice := resp.Choices[0]
		if len(choice.ToolCalls) == 0 {
			return choice.Content, nil
		}
		assistant := llms.MessageContent{Role: llms.ChatMessageTypeAI}
		for _, call := range choice.ToolCalls {
			assistant.Parts = append(assistant.Parts, call)
		}
		messages = append(messages, assistant)
		for _, call := range choice.ToolCalls {
			var args struct {
				OrderID string `json:"order_id"`
			}
			if err := json.Unmarshal([]byte(call.FunctionCall.Arguments), &args); err != nil {
				return "", fmt.Errorf("tool arguments: %w", err)
			}
			messages = append(messages, llms.MessageContent{
				Role: llms.ChatMessageTypeTool,
				Parts: []llms.ContentPart{llms.ToolCallResponse{
					ToolCallID: call.ID,
					Name:       call.FunctionCall.Name,
					Content:    getOrderStatus(args.OrderID),
				}},
			})
		}
	}
	return "Stopped: too many steps.", nil
}

func main() {
	llm, err := openai.New(openai.WithModel(env("OPENAI_MODEL", "gpt-4o-mini")))
	if err != nil {
		log.Fatalf("openai: %v", err)
	}

	http.HandleFunc("POST /run", func(w http.ResponseWriter, r *http.Request) {
		var req struct {
			Prompt string `json:"prompt"`
		}
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			http.Error(w, err.Error(), http.StatusBadRequest)
			return
		}
		answer, err := ask(r.Context(), llm, req.Prompt)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(map[string]string{"answer": answer})
	})

	addr := ":" + env("PORT", "8000")
	log.Printf("listening on %s", addr)
	log.Fatal(http.ListenAndServe(addr, nil))
}

func env(key, def string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return def
}
