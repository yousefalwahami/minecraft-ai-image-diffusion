package com.ai_voxel_image_diffusion.command;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.context.CommandContext;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.concurrent.CompletableFuture;

public class BuildCommand {

    public static void register(CommandDispatcher<CommandSourceStack> dispatcher) {
        dispatcher.register(
            Commands.literal("build")
                .then(Commands.argument("description", StringArgumentType.greedyString())
                    .executes(BuildCommand::executeBuild))
        );
    }

    private static int executeBuild(CommandContext<CommandSourceStack> context) {
        CommandSourceStack source = context.getSource();
        String description = StringArgumentType.getString(context, "description");
        source.sendSuccess(() -> Component.literal("[Build] Sending request: \"" + description + "\"..."), false);

        CompletableFuture.runAsync(() -> {
            try {
                String body = sendGenerateRequest(description);
                JsonObject jsonResponse = JsonParser.parseString(body).getAsJsonObject();

                if (!jsonResponse.has("blocks")) {
                    source.getServer().execute(() ->
                        source.sendFailure(Component.literal("[Build] Server response missing 'blocks'")));
                    return;
                }

                source.getServer().execute(() -> BuildPlanner.plan(source, jsonResponse));

            } catch (Exception e) {
                source.getServer().execute(() ->
                    source.sendFailure(Component.literal("[Build] HTTP request failed: " + e.getMessage())));
            }
        });

        return 1;
    }

    private static String sendGenerateRequest(String description) throws Exception {
        String json = "{\"prompt\":\"" + description.replace("\"", "\\\"") + "\"}";
        HttpClient client = HttpClient.newBuilder()
                .version(HttpClient.Version.HTTP_1_1)
                .build();
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create("http://localhost:8000/generate"))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(json))
                .build();
        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());

        if (response.statusCode() != 200) {
            throw new RuntimeException("Server error (HTTP " + response.statusCode() + "): " + response.body());
        }
        return response.body();
    }
}
