package com.ai_voxel_image_diffusion.command;

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
                String json = "{\"prompt\":\"" + description.replace("\"", "\\\"") + "\"}";
                HttpClient client = HttpClient.newHttpClient();
                HttpRequest request = HttpRequest.newBuilder()
                        .uri(URI.create("http://localhost:8000/generate"))
                        .header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofString(json))
                        .build();

                HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
                String body = response.body();

                // Switch back to the main server thread for Minecraft interactions
                source.getServer().execute(() -> {
                    source.sendSuccess(() -> Component.literal("[Build] Response: " + body), false);

                    // Run WorldEdit's paste command as the player
                    try {
                        source.getServer().getCommands().performPrefixedCommand(source, "paste");
                    } catch (Exception e) {
                        source.sendFailure(Component.literal("[Build] WorldEdit paste failed: " + e.getMessage()));
                    }
                });

            } catch (Exception e) {
                source.getServer().execute(() ->
                    source.sendFailure(Component.literal("[Build] HTTP request failed: " + e.getMessage()))
                );
            }
        });

        return 1;
    }
}
