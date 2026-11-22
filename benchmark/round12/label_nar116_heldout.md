# Held-out labels for `NAR116`

The ten methods below are from GTNH repositories at the last commit before 2023, and their order is random. None of
the ten is in the first set of 14. A javadoc above a method is replaced with the line `(javadoc removed)`. Each method has 10 lines of code
before and after, and a `>` in the margin marks the lines of the method. Label each method **Y** (needs a javadoc) or
**N** (doesn't). Reply in one line, such as `1N 2Y 3N`. Add a note to any item.

Your labels of 2026-11-21 are saved. Item 4 now shows the whole method: the first version of this file marked only the
first 2 lines of the signature.

1. `GTSU`, `GTSUBlock.java`

   ```java
    267  	    	if (te.wrenchCanSetFacing(null, newFacing)) {
    268  	    		te.setFacing(newFacing);
    269  	    	}
    270              return true;
    271  	    }
    272  	    return false;
    273  	}
    274
    275
    276      @Override
   >277      public void breakBlock(World world, int xCoord, int yCoord, int zCoord, Block block, int par6) {
   >278          if (world.isRemote) {
   >279              return;
   >280          }
   >281          TileEntity tile = world.getTileEntity(xCoord, yCoord, zCoord);
   >282          if (tile instanceof IInventory) {
   >283              IInventory inventory = (IInventory)tile;
   >284              for (int j1 = 0; j1 < inventory.getSizeInventory(); ++j1) {
   >285                  ItemStack itemstack = inventory.getStackInSlot(j1);
   >286                  if (itemstack != null) {
   >287                      float f = world.rand.nextFloat() * 0.8F + 0.1F;
   >288                      float f1 = world.rand.nextFloat() * 0.8F + 0.1F;
   >289                      float f2 = world.rand.nextFloat() * 0.8F + 0.1F;
   >290                      while (itemstack.stackSize > 0) {
   >291                          int k1 = world.rand.nextInt(21) + 10;
   >292                          if (k1 > itemstack.stackSize) {
   >293                              k1 = itemstack.stackSize;
   >294                          }
   >295                          itemstack.stackSize -= k1;
   >296                          EntityItem entityitem = new EntityItem(world, xCoord + f, yCoord + f1, zCoord + f2, new ItemStack(itemstack.getItem(), k1, itemstack.getItemDamage()));
   >297                          if (itemstack.hasTagCompound()) {
   >298                              entityitem.getEntityItem().setTagCompound((NBTTagCompound) itemstack.getTagCompound().copy());
   >299                          }
   >300                          entityitem.motionX = world.rand.nextGaussian() * 0.05F;
   >301                          entityitem.motionY = world.rand.nextGaussian() * 0.05F + 0.2F;
   >302                          entityitem.motionZ = world.rand.nextGaussian() * 0.05F;
   >303                          world.spawnEntityInWorld(entityitem);
   >304                      }
   >305                  }
   >306              }
   >307              world.func_147453_f(xCoord, yCoord, zCoord, block);
   >308          }
   >309          super.breakBlock(world, xCoord, yCoord, zCoord, block, par6);
   >310      }
    311
    312  }
    313
   ```

2. `EndlessIDs`, `ItemBiomePainterMixin.java`

   ```java
    12  import net.minecraft.entity.player.EntityPlayer;
    13  import net.minecraft.item.ItemStack;
    14  import net.minecraft.nbt.NBTTagCompound;
    15  import net.minecraft.world.World;
    16  import net.minecraft.world.chunk.Chunk;
    17
    18  @Mixin(ItemBiomePainter.class)
    19  public abstract class ItemBiomePainterMixin {
    20      (javadoc removed)
    21      @Overwrite
   >22      public boolean onItemUse(ItemStack par1ItemStack, EntityPlayer par2EntityPlayer, World par3World, int par4, int par5, int par6, int par7, float par8, float par9, float par10) {
   >23          if (!par2EntityPlayer.inventory.hasItem(ModItems.biomeCapsule)) {
   >24              return false;
   >25          } else if (par3World.isRemote) {
   >26              return true;
   >27          } else {
   >28              for(int i = 0; i < par2EntityPlayer.inventory.getSizeInventory(); ++i) {
   >29                  ItemStack is = par2EntityPlayer.inventory.getStackInSlot(i);
   >30                  if (is != null && is.getItem() instanceof ItemBiomeCapsule && is.getItemDamage() != 0) {
   >31                      NBTTagCompound nbt = is.stackTagCompound;
   >32                      if (nbt == null) {
   >33                          nbt = is.stackTagCompound = new NBTTagCompound();
   >34                      }
   >35
   >36                      int charges = nbt.getInteger("charges");
   >37                      if (charges > 0 || par2EntityPlayer.capabilities.isCreativeMode) {
   >38                          Chunk c = par3World.getChunkFromBlockCoords(par4, par6);
   >39                          int biomeID = is.getItemDamage() - 1;
   >40                          short[] biomeArray = ((IChunkMixin)c).getBiomeShortArray(); //changed
   >41                          if ((biomeArray[(par6 & 15) << 4 | par4 & 15] & 255) != biomeID) {
   >42                              biomeArray[(par6 & 15) << 4 | par4 & 15] = (short)(biomeID & 0xFFFF); //changed
   >43                              ((IChunkMixin)c).setBiomeShortArray(biomeArray); //changed
   >44                              if (!par2EntityPlayer.capabilities.isCreativeMode) {
   >45                                  nbt.setInteger("charges", charges - 1);
   >46                                  par2EntityPlayer.inventoryContainer.detectAndSendChanges();
   >47                              }
   >48
   >49                              PacketHandler.INSTANCE.sendToDimension(new MessagePaintBiome(par4, par5, par6, par3World.provider.dimensionId, biomeID), par3World.provider.dimensionId);
   >50                          }
   >51                      }
   >52
   >53                      return true;
   >54                  }
   >55              }
   >56
   >57              return false;
   >58          }
   >59      }
    60  }
    61
   ```

3. `Prism`, `Prism.java`

   ```java
    126          configuration = new Configuration(getPath());
    127          Sponge.getRegistry().registerModule(PrismEvent.class, PrismEvents.REGISTRY_MODULE);
    128      }
    129
    130      @Listener
    131      public void onPreInitialization(GamePreInitializationEvent event) {
    132          getConfiguration().loadConfiguration();
    133      }
    134
    135      @Listener
   >136      public void onInitialization(GameInitializationEvent event) {
   >137          // Register FlagHandlers
   >138          registerFlagHandler(new FlagClean());
   >139          registerFlagHandler(new FlagDrain());
   >140          registerFlagHandler(new FlagExtended());
   >141          registerFlagHandler(new FlagNoGroup());
   >142          registerFlagHandler(new FlagOrder());
   >143
   >144          // Register ParameterHandlers
   >145          registerParameterHandler(new ParameterBlock());
   >146          registerParameterHandler(new ParameterCause());
   >147          registerParameterHandler(new ParameterEventName());
   >148          registerParameterHandler(new ParameterPlayer());
   >149          registerParameterHandler(new ParameterRadius());
   >150          registerParameterHandler(new ParameterTime());
   >151
   >152          // Register Commands
   >153          Sponge.getCommandManager().register(this, PrismCommands.getCommand(), Reference.ID, "pr");
   >154
   >155          // Register Listeners
   >156          Sponge.getEventManager().registerListeners(getPluginContainer(), new ChangeBlockListener());
   >157          Sponge.getEventManager().registerListeners(getPluginContainer(), new EntityListener());
   >158          Sponge.getEventManager().registerListeners(getPluginContainer(), new InventoryListener());
   >159
   >160          // Events required for internal operation
   >161          Sponge.getEventManager().registerListeners(getPluginContainer(), new RequiredInteractListener());
   >162      }
    163
    164      @Listener
    165      public void onPostInitialization(GamePostInitializationEvent event) {
    166          getConfiguration().saveConfiguration();
    167      }
    168
    169      @Listener
    170      public void onStartedServer(GameStartedServerEvent event) {
    171          String engine = getConfig().getStorageCategory().getEngine();
    172          try {
   ```

4. `Realistic-World-Gen`, `RealisticBiomeDuneValley.java`

   ```java
     31      private SurfaceBase riverSurface;
     32
     33      public RealisticBiomeDuneValley() {
     34          super(0, RWGBiomes.baseHotDesert, RealisticBiomeBase.coastDunes, RWGBiomes.baseRiverOasis);
     35          terrain = new TerrainDunes();
     36          surface = new SurfaceDesert(Blocks.sand, Blocks.sand, Blocks.sandstone, Blocks.stone, Blocks.cobblestone);
     37          riverSurface = new SurfaceRiverOasis();
     38      }
     39
     40      @Override
   > 41      public void rDecorate(
   > 42              World world,
   > 43              Random rand,
   > 44              int chunkX,
   > 45              int chunkY,
   > 46              NoiseGenerator perlin,
   > 47              CellNoise cell,
   > 48              float strength,
   > 49              float river) {
   > 50          if (rand.nextInt((int) (2f / strength)) == 0) {
   > 51              int i1 = chunkX + rand.nextInt(16) + 8;
   > 52              int j1 = chunkY + rand.nextInt(16) + 8;
   > 53              int k1 = world.getHeightValue(i1, j1);
   > 54              if (k1 < 85) {
   > 55                  (new DecoBlob(Blocks.cobblestone, 0)).generate(world, rand, i1, k1, j1);
   > 56              }
   > 57          }
   > 58
   > 59          for (int k18 = 0; k18 < 12f * strength; k18++) {
   > 60              int k21 = chunkX + rand.nextInt(16) + 8;
   > 61              int j23 = rand.nextInt(160);
   > 62              int k24 = chunkY + rand.nextInt(16) + 8;
   > 63              (new DecoCacti(false)).generate(world, rand, k21, j23, k24);
   > 64          }
   > 65
   > 66          for (int i15 = 0; i15 < 3f * strength; i15++) {
   > 67              int i17 = chunkX + rand.nextInt(16) + 8;
   > 68              int i20 = rand.nextInt(160);
   > 69              int l22 = chunkY + rand.nextInt(16) + 8;
   > 70              (new WorldGenDeadBush(Blocks.deadbush)).generate(world, rand, i17, i20, l22);
   > 71          }
   > 72
   > 73          if (river > 0.7f) {
   > 74              if (river > 0.86f) {
   > 75                  for (int b33 = 0; b33 < 10f * strength; b33++) {
   > 76                      int j6 = chunkX + rand.nextInt(16) + 8;
   > 77                      int k10 = chunkY + rand.nextInt(16) + 8;
   > 78                      int z52 = world.getHeightValue(j6, k10);
   > 79
   > 80                      if (z52 < 100f || (z52 < 120f && rand.nextInt(10) == 0)) {
   > 81                          WorldGenerator worldgenerator =
   > 82                                  rand.nextInt(4) != 0 ? new WorldGenShrub(0, 0) : new DecoSavannah(1);
   > 83                          worldgenerator.setScale(1.0D, 1.0D, 1.0D);
   > 84                          worldgenerator.generate(world, rand, j6, z52, k10);
   > 85                      }
   > 86                  }
   > 87              }
   > 88
   > 89              for (int k18 = 0; k18 < 12f * strength; k18++) {
   > 90                  int k21 = chunkX + rand.nextInt(16) + 8;
   > 91                  int j23 = rand.nextInt(160);
   > 92                  int k24 = chunkY + rand.nextInt(16) + 8;
   > 93                  if (j23 < 120f) {
   > 94                      (new DecoCacti(false)).generate(world, rand, k21, j23, k24);
   > 95                  }
   > 96              }
   > 97
   > 98              for (int f25 = 0; f25 < 2f * strength; f25++) {
   > 99                  int i18 = chunkX + rand.nextInt(16) + 8;
   >100                  int i23 = chunkY + rand.nextInt(16) + 8;
   >101                  (new WorldGenReed()).generate(world, rand, i18, 60 + rand.nextInt(8), i23);
   >102              }
   >103
   >104              if (rand.nextInt(28) == 0) {
   >105                  int j16 = chunkX + rand.nextInt(16) + 8;
   >106                  int j18 = rand.nextInt(128);
   >107                  int j21 = chunkY + rand.nextInt(16) + 8;
   >108                  (new WorldGenPumpkin()).generate(world, rand, j16, j18, j21);
   >109              }
   >110
   >111              for (int f23 = 0; f23 < 3; f23++) {
   >112                  int j15 = chunkX + rand.nextInt(16) + 8;
   >113                  int j17 = rand.nextInt(128);
   >114                  int j20 = chunkY + rand.nextInt(16) + 8;
   >115                  (new DecoFlowers(new int[] {9, 9, 9, 9, 3, 3, 3, 3, 3, 2, 2, 2, 11, 11, 11}))
   >116                          .generate(world, rand, j15, j17, j20);
   >117              }
   >118
   >119              for (int l14 = 0; l14 < 15; l14++) {
   >120                  int l19 = chunkX + rand.nextInt(16) + 8;
   >121                  int k22 = rand.nextInt(128);
   >122                  int j24 = chunkY + rand.nextInt(16) + 8;
   >123
   >124                  if (rand.nextInt(6) == 0) {
   >125                      (new DecoGrass(Blocks.double_plant, 2)).generate(world, rand, l19, k22, j24);
   >126                  } else {
   >127                      (new DecoGrass(Blocks.tallgrass, 1)).generate(world, rand, l19, k22, j24);
   >128                  }
   >129              }
   >130          }
   >131      }
    132
    133      public float rNoise(NoiseGenerator perlin, CellNoise cell, int x, int y, float ocean, float border, float river) {
    134          return terrain.generateNoise(perlin, cell, x, y, ocean, border, river);
    135      }
    136
    137      public void rReplace(
    138              Block[] blocks,
    139              byte[] metadata,
    140              int i,
    141              int j,
   ```

5. `Prism`, `BlockResult.java`

   ```java
     93              return ActionableResult.skipped(SkipReason.UNKNOWN);
     94          }
     95
     96          // Final block in this space.
     97          BlockSnapshot resultingBlock = location.getBlock().snapshotFor(location);
     98
     99          return ActionableResult.success(new Transaction<>(original, resultingBlock));
    100
    101      }
    102
   >103      public DataView formatBlockData(DataView finalBlock, @Nonnull Object optionalLocation) {
   >104          Preconditions.checkNotNull(optionalLocation, "The location you are formatting cannot be null.");
   >105          DataView location = (DataView) optionalLocation;
   >106          DataView position = DataContainer.createNew();
   >107          position.set(DataQueries.X, location.get(DataQueries.X).get());
   >108          position.set(DataQueries.Y, location.get(DataQueries.Y).get());
   >109          position.set(DataQueries.Z, location.get(DataQueries.Z).get());
   >110          finalBlock.set(DataQueries.Position, position);
   >111          finalBlock.set(DataQueries.WorldUuid, location.get(DataQueries.WorldUuid).get());
   >112
   >113          int blockStateVersion = finalBlock.getInt(DataQueries.BlockState.then(DataQueries.ContentVersion)).orElse(1);
   >114          if (blockStateVersion == 1) {
   >115              // Unsafe data includes coordinates
   >116              Optional<Object> optionalUnsafeData = finalBlock.get(DataQueries.UnsafeData);
   >117              if (optionalUnsafeData.isPresent()) {
   >118                  DataView unsafeData = (DataView) optionalUnsafeData.get();
   >119                  unsafeData.set(DataQueries.X, location.get(DataQueries.X).get());
   >120                  unsafeData.set(DataQueries.Y, location.get(DataQueries.Y).get());
   >121                  unsafeData.set(DataQueries.Z, location.get(DataQueries.Z).get());
   >122                  finalBlock.set(DataQueries.UnsafeData, unsafeData);
   >123              }
   >124          }
   >125
   >126          return finalBlock;
   >127      }
    128
    129      @Override
    130      public ActionableResult restore() {
    131
    132          Optional<Object> optionalFinal = data.get(DataQueries.ReplacementBlock);
    133          if (!optionalFinal.isPresent()) {
    134              return ActionableResult.skipped(SkipReason.INVALID);
    135          }
    136
    137          // Our data is stored with a different structure, so we'll need
   ```

6. `BiomesOPlenty`, `MessageSpawnParticle.java`

   ```java
    60  		buf.writeFloat(this.posY);
    61  		buf.writeFloat(this.posZ);
    62  		buf.writeFloat(this.offsetX);
    63  		buf.writeFloat(this.offsetY);
    64  		buf.writeFloat(this.offsetZ);
    65  		buf.writeFloat(this.velocity);
    66  		buf.writeInt(this.amount);
    67  	}
    68
    69  	@Override
   >70  	public IMessage onMessage(MessageSpawnParticle message, MessageContext ctx)
   >71  	{
   >72          if (this.amount == 0)
   >73          {
   >74              double d0 = (double)(this.velocity * this.offsetX);
   >75              double d2 = (double)(this.velocity * this.offsetY);
   >76              double d4 = (double)(this.velocity * this.offsetZ);
   >77              //this.clientWorldController.spawnParticle(this.particleName, this.posX, this.posY, this.posZ, d0, d2, d4);
   >78          }
   >79          else
   >80          {
   >81              for (int i = 0; i < this.amount; ++i)
   >82              {
   >83                  double offsetX = this.random.nextGaussian() * (double)this.offsetX;
   >84                  double offsetY = this.random.nextGaussian() * (double)this.offsetY;
   >85                  double offsetZ = this.random.nextGaussian() * (double)this.offsetZ;
   >86                  double d6 = this.random.nextGaussian() * (double)this.velocity;
   >87                  double d7 = this.random.nextGaussian() * (double)this.velocity;
   >88                  double d8 = this.random.nextGaussian() * (double)this.velocity;
   >89                  //this.clientWorldController.spawnParticle(this.particleName, this.posX + offsetX, this.posY + offsetY, this.posZ + offsetZ, d6, d7, d8);
   >90              }
   >91          }
   >92
   >93  		return null;
   >94  	}
    95  }
    96
   ```

7. `CraftGuide`, `RecipeTemplateBuilderImplementation.java`

   ```java
    366  			renderer.renderRect(this.x + x, this.y + y, w, h, texture);
    367  		}
    368
    369  		@Override
    370  		public ItemFilter getClickedFilter(int x, int y, Object[] data, int dataIndex)
    371  		{
    372  			return null;
    373  		}
    374
    375  		@Override
   >376  		public boolean isPointInBounds(int x, int y, Object[] data, int dataIndex)
   >377  		{
   >378  			return false;
   >379  		}
    380
    381  		@Override
    382  		public List<String> getTooltip(int x, int y, Object[] data, int dataIndex)
    383  		{
    384  			return null;
    385  		}
    386
    387  		@Override
    388  		public boolean matches(ItemFilter filter, Object[] data, int dataIndex, SlotType type)
    389  		{
   ```

8. `BiomesOPlenty`, `ItemBOPBucket.java`

   ```java
    103
    104              if (this.tryPlaceContainedLiquid(itemStack, world, x, y, z) && !player.capabilities.isCreativeMode)
    105              {
    106                  return new ItemStack(Items.bucket);
    107              }
    108  		}
    109
    110  		return itemStack;
    111  	}
    112
   >113      public boolean tryPlaceContainedLiquid(ItemStack itemStack, World world, int x, int y, int z)
   >114      {
   >115      	FluidStack fluid = this.getFluid(itemStack);
   >116
   >117          if (fluid == null || fluid.amount == 0)
   >118          {
   >119              return false;
   >120          }
   >121          else
   >122          {
   >123
   >124              Material material = world.getBlock(x, y, z).getMaterial();
   >125              boolean isSolid = material.isSolid();
   >126
   >127              if (!world.isAirBlock(x, y, z) && isSolid)
   >128              {
   >129                  return false;
   >130              }
   >131              else
   >132              {
   >133              	if (!world.isRemote && !isSolid && !material.isLiquid())
   >134              	{
   >135              		world.func_147480_a(x, y, z, true);
   >136              	}
   >137
   >138              	int meta = fluid.getFluid() == BOPCFluids.honey ? 7 : 0;
   >139
   >140              	world.setBlock(x, y, z, fluid.getFluid().getBlock(), meta, 3);
   >141              }
   >142
   >143              return true;
   >144          }
   >145      }
    146
    147  	@Override
    148      public void getSubItems(Item item, CreativeTabs creativeTabs, List list)
    149  	{
    150  		ItemStack fluid = new ItemStack(item);
    151
    152  		this.fill(fluid, new FluidStack(BOPCFluids.poison, FluidContainerRegistry.BUCKET_VOLUME), true); list.add(fluid);
    153  		fluid = new ItemStack(item);
    154  		this.fill(fluid, new FluidStack(BOPCFluids.blood, FluidContainerRegistry.BUCKET_VOLUME), true); list.add(fluid);
    155  		fluid = new ItemStack(item);
   ```

9. `SpongePoweredMixinUpstream`, `SignaturePrinter.java`

   ```java
    281       * @param type Type to generate a friendly name for
    282       * @param box True to return the equivalent boxing type for primitives
    283       * @return String representation of the specified type, eg "int" for an
    284       *         integer primitive or "String" for java.lang.String
    285       */
    286      public static String getTypeName(Type type, boolean box) {
    287          return SignaturePrinter.getTypeName(type, box, false);
    288      }
    289
    290      (javadoc removed)
   >291      public static String getTypeName(Type type, boolean box, boolean fullyQualified) {
   >292          if (type == null) {
   >293              return "{null?}";
   >294          }
   >295          switch (type.getSort()) {
   >296              case Type.VOID:    return box ? "Void"      : "void";
   >297              case Type.BOOLEAN: return box ? "Boolean"   : "boolean";
   >298              case Type.CHAR:    return box ? "Character" : "char";
   >299              case Type.BYTE:    return box ? "Byte"      : "byte";
   >300              case Type.SHORT:   return box ? "Short"     : "short";
   >301              case Type.INT:     return box ? "Integer"   : "int";
   >302              case Type.FLOAT:   return box ? "Float"     : "float";
   >303              case Type.LONG:    return box ? "Long"      : "long";
   >304              case Type.DOUBLE:  return box ? "Double"    : "double";
   >305              case Type.ARRAY:   return SignaturePrinter.getTypeName(type.getElementType(), box, fullyQualified) + SignaturePrinter.arraySuffix(type);
   >306              case Type.OBJECT:
   >307                  String typeName = type.getClassName();
   >308                  if (!fullyQualified) {
   >309                      typeName = typeName.substring(typeName.lastIndexOf('.') + 1);
   >310                  }
   >311                  return typeName;
   >312              default:
   >313                  return "Object";
   >314          }
   >315      }
    316
    317      private static String arraySuffix(Type type) {
    318          return Strings.repeat("[]", type.getDimensions());
    319      }
    320
    321
    322      private static StringBuilder appendArraySuffix(StringBuilder sb, Type type) {
    323          for (int i = 0; i < type.getDimensions(); i++) {
    324              sb.append("[]");
    325          }
   ```

10. `Galaxy-Space-GTNH`, `CeresBlockWeb.java`

   ```java
    25          this.setBlockTextureName("galaxyspace:ceres/ceresweb");
    26      }
    27
    28      @Override
    29      @SideOnly(Side.CLIENT)
    30      public CreativeTabs getCreativeTabToDisplayOn() {
    31          return GalaxySpace.tabBlocks;
    32      }
    33
    34      @Override
   >35      public boolean isTerraformable(final World world, final int x, final int y, final int z) {
   >36          return false;
   >37      }
    38
    39      @Override
    40      public void onEntityCollidedWithBlock(
    41              final World world, final int x, final int y, final int z, final Entity living) {
    42          living.setInWeb();
    43          if (world.provider instanceof IGalacticraftWorldProvider) {
    44              if (living instanceof EntityPlayer) {
    45                  if (living instanceof EntityPlayerMP) {
    46                      final EntityPlayerMP player = (EntityPlayerMP) living;
    47                      player.addPotionEffect(new PotionEffect(Potion.wither.id, 80));
   ```

