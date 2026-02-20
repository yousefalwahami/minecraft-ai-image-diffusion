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
                String json = "{\"prompt\":\"" + description.replace("\"", "\\\"") + "\"}";
                HttpClient client = HttpClient.newHttpClient();
                HttpRequest request = HttpRequest.newBuilder()
                        .uri(URI.create("http://localhost:8000/generate"))
                        .header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofString(json))
                        .build();

                HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
                String body = response.body();

                // Parse schematic_path from JSON response, e.g. {"schematic_path": "test.schem"}
                JsonObject json2 = JsonParser.parseString(body).getAsJsonObject();
                String schematicPath = json2.get("schematic_path").getAsString();
                // WorldEdit expects the name without the .schem extension
                String schematicName = schematicPath.endsWith(".schem")
                        ? schematicPath.substring(0, schematicPath.length() - 6)
                        : schematicPath;

                // Switch back to the main server thread for Minecraft interactions
                source.getServer().execute(() -> {
                    source.sendSuccess(() -> Component.literal("[Build] Loading schematic: " + schematicName), false);

                    try {
                        // Load the schematic into the WorldEdit clipboard
                        source.getServer().getCommands().performPrefixedCommand(source, "//schem load " + schematicName);
                        // Paste it at the player's position
                        source.getServer().getCommands().performPrefixedCommand(source, "//paste");
                        source.sendSuccess(() -> Component.literal("[Build] Pasted \"" + schematicName + "\" successfully."), false);
                    } catch (Exception e) {
                        source.sendFailure(Component.literal("[Build] WorldEdit command failed: " + e.getMessage()));
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
