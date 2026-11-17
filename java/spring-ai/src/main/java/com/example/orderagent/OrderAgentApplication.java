package com.example.orderagent;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Order-status agent built with Spring AI, served over HTTP.
 *
 * <p>POST /run {"prompt": "What's the status of order 42?"} -> {"answer": "..."}. Needs
 * OPENAI_API_KEY. Run: mvn spring-boot:run
 */
@SpringBootApplication
public class OrderAgentApplication {

  public static void main(String[] args) {
    SpringApplication.run(OrderAgentApplication.class, args);
  }
}
