// Order-status agent built with Microsoft Agent Framework, served over HTTP.
//
// POST /run {"prompt": "What's the status of order 42?"} -> {"answer": "..."}
// Needs OPENAI_API_KEY. Run: dotnet run

using System.ComponentModel;
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;
using OpenAI;

var apiKey = Environment.GetEnvironmentVariable("OPENAI_API_KEY")
    ?? throw new InvalidOperationException("OPENAI_API_KEY is not set");
var model = Environment.GetEnvironmentVariable("OPENAI_MODEL") ?? "gpt-4o-mini";

AIAgent agent = new OpenAIClient(apiKey)
    .GetChatClient(model)
    .AsIChatClient()
    .AsAIAgent(
        instructions: "You are a customer support agent. Use your tools to answer questions about orders.",
        tools: [AIFunctionFactory.Create(OrderTools.GetOrderStatus)]);

var builder = WebApplication.CreateBuilder(args);
builder.WebHost.UseUrls($"http://0.0.0.0:{Environment.GetEnvironmentVariable("PORT") ?? "8000"}");
var app = builder.Build();

app.MapPost("/run", async (RunRequest request) =>
{
    var response = await agent.RunAsync(request.Prompt);
    return Results.Json(new { answer = response.Text });
});

app.Run();

record RunRequest(string Prompt);

static class OrderTools
{
    [Description("Look up the shipping status of an order by its id.")]
    public static string GetOrderStatus([Description("The order id")] string orderId) =>
        $"Order {orderId}: shipped, arriving Friday.";
}
