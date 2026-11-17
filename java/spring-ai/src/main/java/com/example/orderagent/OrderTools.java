package com.example.orderagent;

import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.stereotype.Component;

@Component
public class OrderTools {

  @Tool(description = "Look up the shipping status of an order by its id.")
  public String getOrderStatus(@ToolParam(description = "The order id") String orderId) {
    return "Order " + orderId + ": shipped, arriving Friday.";
  }
}
