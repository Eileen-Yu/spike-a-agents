// Command eino serves an order-status agent built with Eino's ReAct agent.
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

	"github.com/cloudwego/eino-ext/components/model/openai"
	"github.com/cloudwego/eino/components/tool"
	"github.com/cloudwego/eino/components/tool/utils"
	"github.com/cloudwego/eino/compose"
	"github.com/cloudwego/eino/flow/agent/react"
	"github.com/cloudwego/eino/schema"
)

const system = "You are a customer support agent. Use your tools to answer questions about orders."

type orderRequest struct {
	OrderID string `json:"order_id" jsonschema:"description=The order id"`
}

func getOrderStatus(_ context.Context, in orderRequest) (string, error) {
	return fmt.Sprintf("Order %s: shipped, arriving Friday.", in.OrderID), nil
}

func newAgent(ctx context.Context) (*react.Agent, error) {
	model, err := openai.NewChatModel(ctx, &openai.ChatModelConfig{
		APIKey: os.Getenv("OPENAI_API_KEY"),
		Model:  env("OPENAI_MODEL", "gpt-4o-mini"),
	})
	if err != nil {
		return nil, fmt.Errorf("openai chat model: %w", err)
	}
	orderTool, err := utils.InferTool("get_order_status", "Look up the shipping status of an order by its id.", getOrderStatus)
	if err != nil {
		return nil, fmt.Errorf("tool: %w", err)
	}
	return react.NewAgent(ctx, &react.AgentConfig{
		ToolCallingModel: model,
		ToolsConfig:      compose.ToolsNodeConfig{Tools: []tool.BaseTool{orderTool}},
		MaxStep:          8,
	})
}

func main() {
	ctx := context.Background()
	agent, err := newAgent(ctx)
	if err != nil {
		log.Fatal(err)
	}

	http.HandleFunc("POST /run", func(w http.ResponseWriter, r *http.Request) {
		var req struct {
			Prompt string `json:"prompt"`
		}
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			http.Error(w, err.Error(), http.StatusBadRequest)
			return
		}
		msg, err := agent.Generate(r.Context(), []*schema.Message{
			schema.SystemMessage(system),
			schema.UserMessage(req.Prompt),
		})
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(map[string]string{"answer": msg.Content})
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
