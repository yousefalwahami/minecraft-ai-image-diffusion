package com.ai_voxel_image_diffusion;

import com.ai_voxel_image_diffusion.command.BuildCommand;
import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ExampleMod implements ModInitializer {
	public static final String MOD_ID = "ai_voxel_image_diffusion";
	public static final Logger LOGGER = LoggerFactory.getLogger(MOD_ID);

	@Override
	public void onInitialize() {
		CommandRegistrationCallback.EVENT.register((dispatcher, registryAccess, environment) ->
			BuildCommand.register(dispatcher)
		);

		LOGGER.info("AI Voxel Image Diffusion mod initialized.");
	}
}