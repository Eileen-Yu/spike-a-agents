package com.example.orderagent;

import java.util.Map;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class RunController {

  private final ChatClient chatClient;

  public RunController(ChatClient.Builder builder, OrderTools tools) {
    this.chatClient =
        builder
            .defaultSystem(
                "You are a customer support agent. Use your tools to answer questions about orders.")
            .defaultTools(tools)
            .build();
  }

  public record RunRequest(String prompt) {}

  @PostMapping("/run")
  public Map<String, String> run(@RequestBody RunRequest request) {
    return Map.of("answer", chatClient.prompt().user(request.prompt()).call().content());
  }
}
