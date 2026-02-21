package com.ai_voxel_image_diffusion.command;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.arguments.blocks.BlockStateParser;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.phys.Vec3;

import java.util.ArrayList;
import java.util.List;

public class BuildPlanner {

    /** Distance in blocks from the player to the center of the building. */
    private static final int PLACE_DISTANCE = 10;

    /**
     * Parses the server JSON response, applies rotation to match the player's
     * facing direction, computes the world-space corner, and kicks off the animator.
     */
    public static void plan(CommandSourceStack source, JsonObject jsonResponse) {
        try {
            ServerPlayer player = source.getPlayerOrException();
            Vec3 origin = player.position();
            float yaw = player.getYRot();

            int schemWidth  = jsonResponse.has("width")  ? jsonResponse.get("width").getAsInt()  : 1;
            int schemLength = jsonResponse.has("length") ? jsonResponse.get("length").getAsInt() : 1;
            JsonArray blocksArray = jsonResponse.getAsJsonArray("blocks");

            ServerLevel level = (ServerLevel) player.level();
            HolderLookup<Block> blockLookup = level.registryAccess().lookupOrThrow(Registries.BLOCK);

            List<BuildAnimator.BlockToPlace> blocks = parse(blocksArray, blockLookup);

            // Snap to nearest 90° so blocks always align to a cardinal direction
            float snappedYaw = Math.round(yaw / 90.0f) * 90.0f;
            double rad   = Math.toRadians(snappedYaw);
            double fwdDx = -Math.sin(rad);
            double fwdDz =  Math.cos(rad);
            double perpDx =  Math.cos(rad);
            double perpDz =  Math.sin(rad);

            // Corner so the CENTER of the building is exactly PLACE_DISTANCE blocks ahead, centered L/R
            double cornerX = origin.x + fwdDx * (PLACE_DISTANCE - schemLength / 2.0) - perpDx * (schemWidth / 2.0);
            double cornerY = origin.y;
            double cornerZ = origin.z + fwdDz * (PLACE_DISTANCE - schemLength / 2.0) - perpDz * (schemWidth / 2.0);

            BuildAnimator.start(level, blockLookup, source, blocks,
                    cornerX, cornerY, cornerZ,
                    fwdDx, fwdDz, perpDx, perpDz);

        } catch (Exception e) {
            source.sendFailure(Component.literal("[Build] Failed to plan build: " + e.getMessage()));
        }
    }

    private static List<BuildAnimator.BlockToPlace> parse(
            JsonArray blocksArray, HolderLookup<Block> blockLookup) {

        List<BuildAnimator.BlockToPlace> blocks = new ArrayList<>();
        for (JsonElement el : blocksArray) {
            JsonObject b = el.getAsJsonObject();
            int bx = b.get("x").getAsInt();
            int by = b.get("y").getAsInt();
            int bz = b.get("z").getAsInt();
            String stateStr = b.get("b").getAsString();
            // bx → perp (player's right), bz → fwd (player's forward)
            // No rotation needed — the forward/perp vectors handle orientation
            try {
                BlockStateParser.parseForBlock(blockLookup, stateStr, false);
                blocks.add(new BuildAnimator.BlockToPlace(bx, by, bz, stateStr));
            } catch (Exception ignored) {}
        }
        return blocks;
    }
}
