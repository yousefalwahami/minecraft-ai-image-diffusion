package com.ai_voxel_image_diffusion.command;

import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.arguments.blocks.BlockStateParser;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;

import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.TimeUnit;

public class BuildAnimator {

    public record BlockToPlace(int rx, int ry, int rz, String state) {}

    /**
     * Places blocks from the list in batches, one batch per tick (~50 ms),
     * so the full build takes roughly 10 seconds (200 ticks).
     */
    public static void start(
            ServerLevel level,
            HolderLookup<Block> blockLookup,
            CommandSourceStack source,
            List<BlockToPlace> blocks,
            double cornerX, double cornerY, double cornerZ,
            double fwdDx, double fwdDz,
            double perpDx, double perpDz) {

        int batchSize = Math.max(1, blocks.size() / 200);
        source.sendSuccess(() -> Component.literal("[Build] Placing " + blocks.size() + " blocks..."), false);
        scheduleBatch(level, blockLookup, source, blocks, 0, batchSize,
                cornerX, cornerY, cornerZ, fwdDx, fwdDz, perpDx, perpDz);
    }

    private static void scheduleBatch(
            ServerLevel level, HolderLookup<Block> blockLookup,
            CommandSourceStack source,
            List<BlockToPlace> blocks, int index, int batchSize,
            double cornerX, double cornerY, double cornerZ,
            double fwdDx, double fwdDz, double perpDx, double perpDz) {

        MinecraftServer server = level.getServer();
        server.execute(() -> {
            int end = Math.min(index + batchSize, blocks.size());
            for (int i = index; i < end; i++) {
                BlockToPlace b = blocks.get(i);
                double wx = cornerX + b.rx() * perpDx + b.rz() * fwdDx;
                double wz = cornerZ + b.rx() * perpDz + b.rz() * fwdDz;
                int wy = (int) cornerY + b.ry();
                BlockPos pos = BlockPos.containing(wx, wy, wz);
                try {
                    BlockState state = BlockStateParser.parseForBlock(blockLookup, b.state(), false).blockState();
                    level.setBlock(pos, state, Block.UPDATE_ALL);
                } catch (Exception ignored) {}
            }

            if (end < blocks.size()) {
                CompletableFuture.delayedExecutor(50, TimeUnit.MILLISECONDS)
                    .execute(() -> scheduleBatch(level, blockLookup, source,
                            blocks, end, batchSize,
                            cornerX, cornerY, cornerZ,
                            fwdDx, fwdDz, perpDx, perpDz));
            } else {
                source.sendSuccess(() -> Component.literal("[Build] Done!"), false);
            }
        });
    }
}
