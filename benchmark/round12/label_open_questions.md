# Labels for the open questions Q1, Q3, Q4 and Q5

Every example below is from human code written before 2023, except the examples marked Claude. Each example has 10
lines of code before and after, and a `>` in the margin marks the lines of the example. Reply with one line for each
question, such as `Q1: 1G 2B 3G`. Add a note to any item.

Your label of Q1 item 1 is recorded: G, and the form is not to become an example of the skill.

## Q1. Comments with a reason

Twelve comments from the Python 3.14 standard library. Label each comment **G** (a good comment) or **B** (a bad
comment). From your labels, I derive the form of a Fence.

1. `zipfile/__init__.py:1634`

   ```python
    1624                    file=file)
    1625
    1626      def testzip(self):
    1627          """Read all the files and check the CRC.
    1628
    1629          Return None if all files could be read successfully, or the name
    1630          of the offending file otherwise."""
    1631          chunk_size = 2 ** 20
    1632          for zinfo in self.filelist:
    1633              try:
   >1634                  # Read by chunks, to avoid an OverflowError or a
   >1635                  # MemoryError with very large embedded files.
    1636                  with self.open(zinfo.filename, "r") as f:
    1637                      while f.read(chunk_size):     # Check CRC-32
    1638                          pass
    1639              except BadZipFile:
    1640                  return zinfo.filename
    1641
    1642      def getinfo(self, name):
    1643          """Return the instance of ZipInfo given 'name'."""
    1644          info = self.NameToInfo.get(name)
    1645          if info is None:
   ```

2. `asyncio/base_events.py:1344`

   ```python
    1334                  f'transport {transport!r} is not supported by start_tls()')
    1335
    1336          waiter = self.create_future()
    1337          ssl_protocol = sslproto.SSLProtocol(
    1338              self, protocol, sslcontext, waiter,
    1339              server_side, server_hostname,
    1340              ssl_handshake_timeout=ssl_handshake_timeout,
    1341              ssl_shutdown_timeout=ssl_shutdown_timeout,
    1342              call_connection_made=False)
    1343
   >1344          # Pause early so that "ssl_protocol.data_received()" doesn't
   >1345          # have a chance to get called before "ssl_protocol.connection_made()".
    1346          transport.pause_reading()
    1347
    1348          # gh-142352: move buffered StreamReader data to SSLProtocol
    1349          if server_side:
    1350              from .streams import StreamReaderProtocol
    1351              if isinstance(protocol, StreamReaderProtocol):
    1352                  stream_reader = getattr(protocol, '_stream_reader', None)
    1353                  if stream_reader is not None:
    1354                      buffer = stream_reader._buffer
    1355                      if buffer:
   ```

3. `concurrent/futures/process.py:486`

   ```python
    476                                  "running or pending.")
    477          if cause is not None:
    478              bpe.__cause__ = _RemoteTraceback(
    479                  f"\n'''\n{''.join(cause)}'''")
    480
    481          # Mark pending tasks as failed.
    482          for work_id, work_item in self.pending_work_items.items():
    483              try:
    484                  work_item.future.set_exception(bpe)
    485              except _base.InvalidStateError:
   >486                  # set_exception() fails if the future is cancelled: ignore it.
   >487                  # Trying to check if the future is cancelled before calling
   >488                  # set_exception() would leave a race condition if the future is
   >489                  # cancelled between the check and set_exception().
    490                  pass
    491              # Delete references to object. See issue16284
    492              del work_item
    493          self.pending_work_items.clear()
    494
    495          # Terminate remaining workers forcibly: the queues or their
    496          # locks may be in a dirty state and block forever.
    497          for p in self.processes.values():
    498              p.terminate()
    499
   ```

4. `asyncio/tasks.py:547`

   ```python
    537  async def _cancel_and_wait(fut):
    538      """Cancel the *fut* future or task and wait until it completes."""
    539
    540      loop = events.get_running_loop()
    541      waiter = loop.create_future()
    542      cb = functools.partial(_release_waiter, waiter)
    543      fut.add_done_callback(cb)
    544
    545      try:
    546          fut.cancel()
   >547          # We cannot wait on *fut* directly to make
   >548          # sure _cancel_and_wait itself is reliably cancellable.
    549          await waiter
    550      finally:
    551          fut.remove_done_callback(cb)
    552
    553
    554  class _AsCompletedIterator:
    555      """Iterator of awaitables representing tasks of asyncio.as_completed.
    556
    557      As an asynchronous iterator, iteration yields futures as they finish. As a
    558      plain iterator, new coroutines are yielded that will return or raise the
   ```

5. `logging/handlers.py:1499`

   ```python
    1489          the record to a dict or JSON string, or send a modified copy
    1490          of the record while leaving the original intact.
    1491          """
    1492          # The format operation gets traceback text into record.exc_text
    1493          # (if there's exception data), and also returns the formatted
    1494          # message. We can then use this to replace the original
    1495          # msg + args, as these might be unpickleable. We also zap the
    1496          # exc_info, exc_text and stack_info attributes, as they are no longer
    1497          # needed and, if not None, will typically not be pickleable.
    1498          msg = self.format(record)
   >1499          # bpo-35726: make copy of record to avoid affecting other handlers in the chain.
    1500          record = copy.copy(record)
    1501          record.message = msg
    1502          record.msg = msg
    1503          record.args = None
    1504          record.exc_info = None
    1505          record.exc_text = None
    1506          record.stack_info = None
    1507          return record
    1508
    1509      def emit(self, record):
   ```

6. `asyncio/base_events.py:1695`

   ```python
    1685              raise ValueError(
    1686                  'ssl_shutdown_timeout is only meaningful with ssl')
    1687
    1688          _check_ssl_socket(sock)
    1689
    1690          transport, protocol = await self._create_connection_transport(
    1691              sock, protocol_factory, ssl, '', server_side=True,
    1692              ssl_handshake_timeout=ssl_handshake_timeout,
    1693              ssl_shutdown_timeout=ssl_shutdown_timeout)
    1694          if self._debug:
   >1695              # Get the socket from the transport because SSL transport closes
   >1696              # the old socket and creates a new SSL socket
    1697              sock = transport.get_extra_info('socket')
    1698              logger.debug("%r handled: (%r, %r)", sock, transport, protocol)
    1699          return transport, protocol
    1700
    1701      async def connect_read_pipe(self, protocol_factory, pipe):
    1702          protocol = protocol_factory()
    1703          waiter = self.create_future()
    1704          transport = self._make_read_pipe_transport(pipe, protocol, waiter)
    1705
    1706          try:
   ```

7. `concurrent/futures/process.py:371`

   ```python
    361                      if process_exited:
    362                          with self.shutdown_lock:
    363                              executor._adjust_process_count()
    364                      else:
    365                          executor._idle_worker_semaphore.release()
    366                      del executor
    367
    368              if self.is_shutting_down():
    369                  self.flag_executor_shutting_down()
    370
   >371                  # When only canceled futures remain in pending_work_items, our
   >372                  # next call to wait_result_broken_or_wakeup would hang forever.
   >373                  # This makes sure we have some running futures or none at all.
    374                  self.add_call_item_to_queue()
    375
    376                  # Since no new work items can be added, it is safe to shutdown
    377                  # this thread if there are no pending work items.
    378                  if not self.pending_work_items:
    379                      self.join_executor_internals()
    380                      return
    381
    382      def add_call_item_to_queue(self):
    383          # Fills call_queue with _WorkItems from pending_work_items.
   ```

8. `tarfile.py:833`

   ```python
    823          if member.gid is not None:
    824              new_attrs['gid'] = None
    825          if member.uname is not None:
    826              new_attrs['uname'] = None
    827          if member.gname is not None:
    828              new_attrs['gname'] = None
    829          # Check link destination for 'data'
    830          if member.islnk() or member.issym():
    831              if os.path.isabs(member.linkname):
    832                  raise AbsoluteLinkError(member)
   >833              # A link member that resolves to the destination directory itself
   >834              # would replace it with a (sym)link, redirecting the destination
   >835              # for all subsequent members.
    836              if target_path == dest_path:
    837                  raise OutsideDestinationError(member, target_path)
    838              normalized = os.path.normpath(member.linkname)
    839              if normalized != member.linkname:
    840                  new_attrs['linkname'] = normalized
    841              if member.issym():
    842                  # The symlink is created at `name` with trailing separators
    843                  # stripped, so its target is relative to the directory
    844                  # containing that path.
    845                  link_dir = os.path.dirname(name.rstrip('/' + os.sep))
   ```

9. `weakref.py:470`

   ```python
    460      _shutdown = False
    461      _index_iter = itertools.count()
    462      _dirty = False
    463      _registered_with_atexit = False
    464
    465      class _Info:
    466          __slots__ = ("weakref", "func", "args", "kwargs", "atexit", "index")
    467
    468      def __init__(self, obj, func, /, *args, **kwargs):
    469          if not self._registered_with_atexit:
   >470              # We may register the exit function more than once because
   >471              # of a thread race, but that is harmless
    472              import atexit
    473              atexit.register(self._exitfunc)
    474              finalize._registered_with_atexit = True
    475          info = self._Info()
    476          info.weakref = ref(obj, self)
    477          info.func = func
    478          info.args = args
    479          info.kwargs = kwargs or None
    480          info.atexit = True
    481          info.index = next(self._index_iter)
   ```

10. `socketserver.py:626`

   ```python
    616              """Fork a new subprocess to process the request."""
    617              pid = os.fork()
    618              if pid:
    619                  # Parent process
    620                  if self.active_children is None:
    621                      self.active_children = set()
    622                  self.active_children.add(pid)
    623                  self.close_request(request)
    624                  return
    625              else:
   >626                  # Child process.
   >627                  # This must never return, hence os._exit()!
    628                  status = 1
    629                  try:
    630                      self.finish_request(request, client_address)
    631                      status = 0
    632                  except Exception:
    633                      self.handle_error(request, client_address)
    634                  finally:
    635                      try:
    636                          self.shutdown_request(request)
    637                      finally:
   ```

11. `asyncio/base_events.py:476`

   ```python
    466          self._check_closed()
    467          if self._task_factory is not None:
    468              return self._task_factory(self, coro, **kwargs)
    469
    470          task = tasks.Task(coro, loop=self, **kwargs)
    471          if task._source_traceback:
    472              del task._source_traceback[-1]
    473          try:
    474              return task
    475          finally:
   >476              # gh-128552: prevent a refcycle of
   >477              # task.exception().__traceback__->BaseEventLoop.create_task->task
    478              del task
    479
    480      def set_task_factory(self, factory):
    481          """Set a task factory that will be used by loop.create_task().
    482
    483          If factory is None the default task factory will be set.
    484
    485          If factory is a callable, it should have a signature matching
    486          '(loop, coro, **kwargs)', where 'loop' will be a reference to the active
    487          event loop, 'coro' will be a coroutine object, and **kwargs will be
   ```

12. `queue.py:50`

   ```python
    40  class Queue:
    41      '''Create a queue object with a given maximum size.
    42
    43      If maxsize is <= 0, the queue size is infinite.
    44      '''
    45
    46      def __init__(self, maxsize=0):
    47          self.maxsize = maxsize
    48          self._init(maxsize)
    49
   >50          # mutex must be held whenever the queue is mutating.  All methods
   >51          # that acquire mutex must release it before returning.  mutex
   >52          # is shared between the three conditions, so acquiring and
   >53          # releasing the conditions also acquires and releases mutex.
    54          self.mutex = threading.Lock()
    55
    56          # Notify not_empty whenever an item is added to the queue; a
    57          # thread waiting to get is notified then.
    58          self.not_empty = threading.Condition(self.mutex)
    59
    60          # Notify not_full whenever an item is removed from the queue;
    61          # a thread waiting to put is notified then.
    62          self.not_full = threading.Condition(self.mutex)
    63
   ```

## Q3. Does the method need a javadoc?

Fourteen methods over the threshold of `NAR116` (more than 3 parameters, or more than 20 body lines). A javadoc above
a method is replaced with the line `(javadoc removed)`. Twelve methods are from GTNH repositories at the last commit
before 2023, and two are the methods of NEI PR 1146 (Claude). Label each method **Y** (needs a javadoc) or **N**
(doesn't). I keep the metrics of each method, such as the cyclomatic complexity, apart from this file. Then I check
which metric fits your labels.

1. `BON2`, `DownloadUtils.java`

   ```java
    164              //As well as any errors during download.
    165              //So delete the output if it exists as it's invalid, and return false
    166              if (output.exists())
    167                  output.delete();
    168              e.printStackTrace();
    169          }
    170
    171          return false;
    172      }
    173
   >174      private static boolean downloadFile(URLConnection con, File output, IProgressListener listener) throws IOException {
   >175          try {
   >176              InputStream stream = con.getInputStream();
   >177              int len = con.getContentLength();
   >178              int read = -1;
   >179
   >180              if (listener != null) {
   >181                  String tmp = con.getURL().toString();
   >182                  tmp = tmp.substring(tmp.lastIndexOf('/') + 1, tmp.length());
   >183                  listener.start(len, "Downloading: " + tmp);
   >184              }
   >185
   >186              output.getParentFile().mkdirs();
   >187
   >188              try (FileOutputStream out = new FileOutputStream(output)) {
   >189                  read = IOUtils.copy(stream, out, listener);
   >190              }
   >191
   >192              if (read != len && len != -1) {
   >193                  output.delete();
   >194                  throw new IOException("Failed to read all of data from " + con.getURL() + " got " + read + " expected " + len);
   >195              }
   >196
   >197              return true;
   >198          } catch (IOException e) {
   >199              output.delete();
   >200              throw e;
   >201          }
   >202      }
    203
    204      public static boolean downloadWithCache(URL url, File target, boolean changing, boolean bypassLocal) throws IOException {
    205          return downloadWithCache(url, target, changing, bypassLocal, null);
    206      }
    207
    208      public static boolean downloadWithCache(URL url, File target, boolean changing, boolean bypassLocal, IProgressListener listener) throws IOException {
    209          File md5_file = new File(target.getAbsolutePath() + ".md5");
    210          String actual = target.exists() ? HashFunction.MD5.hash(target) : null;
    211
    212          if (target.exists() && !(changing || bypassLocal)) {
   ```

2. `BiomesOPlenty`, `WorldGenBulbTree.java`

   ```java
    254                      return false;
    255                  }
    256              }
    257          }
    258          else
    259          {
    260              return false;
    261          }
    262      }
    263
   >264  	private void growVines(World world, int x, int y, int z, int flag)
   >265  	{
   >266  		this.setBlockAndNotifyAdequately(world, x, y, z, Blocks.vine, flag);
   >267  		int i1 = 4;
   >268
   >269  		while (true)
   >270  		{
   >271  			--y;
   >272
   >273  			if (world.getBlock(x, y, z).isAir(world, x, y, z) || i1 <= 0)
   >274  			{
   >275  				return;
   >276  			}
   >277
   >278  			this.setBlockAndNotifyAdequately(world, x, y, z, Blocks.vine, flag);
   >279  			--i1;
   >280  		}
   >281  	}
    282  }
    283
   ```

3. `EndlessIDs`, `AnvilChunkLoaderMixin.java`

   ```java
    112                  var17.appendTag(var20);
    113              }
    114
    115              p_75820_3_.setTag("TileTicks", var17);
    116          }
    117
    118      }
    119
    120      (javadoc removed)
    121      @Overwrite
   >122      private Chunk readChunkFromNBT(World p_75823_1_, NBTTagCompound p_75823_2_) {
   >123          int var3 = p_75823_2_.getInteger("xPos");
   >124          int var4 = p_75823_2_.getInteger("zPos");
   >125          Chunk var5 = new Chunk(p_75823_1_, var3, var4);
   >126          var5.heightMap = p_75823_2_.getIntArray("HeightMap");
   >127          var5.isTerrainPopulated = p_75823_2_.getBoolean("TerrainPopulated");
   >128          var5.isLightPopulated = p_75823_2_.getBoolean("LightPopulated");
   >129          var5.inhabitedTime = p_75823_2_.getLong("InhabitedTime");
   >130          NBTTagList var6 = p_75823_2_.getTagList("Sections", 10);
   >131          byte var7 = 16;
   >132          ExtendedBlockStorage[] var8 = new ExtendedBlockStorage[var7];
   >133          boolean var9 = !p_75823_1_.provider.hasNoSky;
   >134
   >135          for (int var10 = 0; var10 < var6.tagCount(); ++var10) {
   >136              NBTTagCompound var11 = var6.getCompoundTagAt(var10);
   >137              byte var12 = var11.getByte("Y");
   >138              ExtendedBlockStorage var13 = new ExtendedBlockStorage(var12 << 4, var9);
   >139              Hooks.readChunkFromNbt((IExtendedBlockStorageMixin) var13, var11);
   >140              var13.setBlockMetadataArray(new NibbleArray(var11.getByteArray("Data"), 4));
   >141              var13.setBlocklightArray(new NibbleArray(var11.getByteArray("BlockLight"), 4));
   >142              if (var9) {
   >143                  var13.setSkylightArray(new NibbleArray(var11.getByteArray("SkyLight"), 4));
   >144              }
   >145
   >146              var13.removeInvalidBlocks();
   >147              var8[var12] = var13;
   >148          }
   >149
   >150          var5.setStorageArrays(var8);
   >151          Hooks.readChunkBiomeArrayFromNbt(var5, p_75823_2_);
   >152          return var5;
   >153      }
    154  }
    155
   ```

4. `NotEnoughItems (PR 1146)`, `MobOverlayScan.java` (Claude)

   ```java
    332          final int highTo = lowTo + span - 1;
    333          if (isAlongX) {
    334              markChunks(lowFrom, lowTo, minZ, minZ + span - 1);
    335              markChunks(highFrom, highTo, minZ, minZ + span - 1);
    336          } else {
    337              markChunks(minX, minX + span - 1, lowFrom, lowTo);
    338              markChunks(minX, minX + span - 1, highFrom, highTo);
    339          }
    340      }
    341
   >342      private void markChunks(int fromX, int toX, int fromZ, int toZ) {
   >343          for (int chunkX = fromX >> CHUNK_SHIFT; chunkX <= toX >> CHUNK_SHIFT; chunkX++) {
   >344              for (int chunkZ = fromZ >> CHUNK_SHIFT; chunkZ <= toZ >> CHUNK_SHIFT; chunkZ++) {
   >345                  markChunk(chunkX, chunkZ);
   >346              }
   >347          }
   >348      }
    349
    350      private void markAllChunks() {
    351          Arrays.fill(chunkVersions, ++chunkVersionCount);
    352      }
    353
    354      private void markChunk(int chunkX, int chunkZ) {
    355          chunkVersions[findChunk(chunkX, chunkZ)] = ++chunkVersionCount;
    356      }
    357
    358      public int findChunk(int chunkX, int chunkZ) {
   ```

5. `CoFHCore`, `BaseMod.java`

   ```java
    215
    216  		private final String _path;
    217
    218  		public LangManager(IResourceManager manager) {
    219
    220  			_path = getAssetDir() + ":language/";
    221  			onResourceManagerReload(manager);
    222  		}
    223
    224  		@Override
   >225  		public void onResourceManagerReload(IResourceManager manager) {
   >226
   >227  			String l = null;
   >228  			try {
   >229  				l = Minecraft.getMinecraft().getLanguageManager().getCurrentLanguage().getLanguageCode();
   >230  			} catch (Throwable t) {
   >231  				_log.catching(Level.WARN, t);
   >232  			}
   >233
   >234  			for (String lang : Arrays.asList("en_US", l)) {
   >235  				if (lang != null) {
   >236  					Properties langPack = new Properties();
   >237  					try {
   >238  						List<IResource> files = manager.getAllResources(new ResourceLocation(_path + lang + ".lang"));
   >239  						for (IResource file : files) {
   >240  							if (file.getInputStream() == null) {
   >241  								_log.warn("A resource pack defines an entry for language '" + lang + "' but the InputStream is null.");
   >242  								continue;
   >243  							}
   >244  							try {
   >245  								loadLanguageFile(langPack, file.getInputStream());
   >246  							} catch (Throwable t) {
   >247  								_log.warn(AbstractLogger.CATCHING_MARKER, "A resource pack has a file for language '" + lang + "' but the file is invalid.", t);
   >248  							}
   >249  						}
   >250  					} catch (Throwable t) {
   >251  						_log.info(AbstractLogger.CATCHING_MARKER, "No language data for '" + lang + "'", t);
   >252  					}
   >253  					loadLanguageFile(lang, langPack);
   >254  				}
   >255  			}
   >256
   >257  			Minecraft.getMinecraft().getLanguageManager().onResourceManagerReload(manager);
   >258  		}
    259  	}
    260
    261  	private class CrashCallable implements ICrashCallable {
    262
    263  		private final String data;
    264
    265  		private CrashCallable(String data) {
    266
    267  			this.data = data;
    268  		}
   ```

6. `Prism`, `PrimitiveArrayCodec.java`

   ```java
     79          } else {
     80              reader.readEndDocument();
     81              throw new BsonInvalidOperationException("Unsupported primitive type");
     82          }
     83
     84          reader.readEndDocument();
     85          return new PrimitiveArray(key, value);
     86      }
     87
     88      @Override
   > 89      public void encode(BsonWriter writer, PrimitiveArray object, EncoderContext encoderContext) {
   > 90          writer.writeStartDocument();
   > 91          writer.writeString("key", object.getKey());
   > 92
   > 93          Object array = object.getArray();
   > 94          if (array instanceof byte[]) {
   > 95              writer.writeName("value");
   > 96              writer.writeStartArray();
   > 97              for (byte value : (byte[]) array) {
   > 98                  byteCodec.encode(writer, value, encoderContext);
   > 99              }
   >100
   >101              writer.writeEndArray();
   >102          } else if (array instanceof int[]) {
   >103              writer.writeName("value");
   >104              writer.writeStartArray();
   >105              for (int value : (int[]) array) {
   >106                  integerCodec.encode(writer, value, encoderContext);
   >107              }
   >108
   >109              writer.writeEndArray();
   >110          } else if (array instanceof long[]) {
   >111              writer.writeName("value");
   >112              writer.writeStartArray();
   >113              for (long value : (long[]) array) {
   >114                  longCodec.encode(writer, value, encoderContext);
   >115              }
   >116
   >117              writer.writeEndArray();
   >118          } else {
   >119              writer.writeEndDocument();
   >120              throw new BsonInvalidOperationException("Unsupported primitive type");
   >121          }
   >122
   >123          writer.writeEndDocument();
   >124      }
    125
    126      @Override
    127      public Class<PrimitiveArray> getEncoderClass() {
    128          return PrimitiveArray.class;
    129      }
    130  }
   ```

7. `GT5-Unofficial-split`, `GT_Cover_Shutter.java`

   ```java
    133
    134      @Override
    135      public boolean letsItemsOut(byte aSide, int aCoverID, int aCoverVariable, int aSlot, ICoverable aTileEntity) {
    136          return aCoverVariable >= 2
    137                  ? aCoverVariable == 2
    138                  : !(aTileEntity instanceof IMachineProgress)
    139                          || ((IMachineProgress) aTileEntity).isAllowedToWork() == (aCoverVariable % 2 == 0);
    140      }
    141
    142      @Override
   >143      public boolean alwaysLookConnected(byte aSide, int aCoverID, int aCoverVariable, ICoverable aTileEntity) {
   >144          return true;
   >145      }
    146
    147      @Override
    148      public int getTickRate(byte aSide, int aCoverID, int aCoverVariable, ICoverable aTileEntity) {
    149          return 0;
    150      }
    151
    152      // GUI stuff
    153
    154      @Override
    155      public boolean hasCoverGUI() {
   ```

8. `GTSU`, `TileEntityGTSU.java`

   ```java
     55  		mChargeSlot = new InvSlotCharge(this, 0, 5);
     56  		mDischargeSlot = new InvSlotDischarge(this, 1, InvSlot.Access.IO, 5, InvSlot.InvSide.BOTTOM);
     57  	}
     58
     59  	public int getChargePercentage()
     60  	{
     61  		return new Double((100.0D / (double)mMaxStorage) * (double)mEnergy).intValue();
     62  	}
     63
     64  	@Override
   > 65  	public void updateEntity()
   > 66  	{
   > 67  		super.updateEntity();
   > 68
   > 69  		boolean needsInvUpdate = false;
   > 70  		if (this.mEnergy >= 1L)
   > 71  		{
   > 72  			double sent = this.mChargeSlot.charge(this.mEnergy);
   > 73
   > 74  			this.mEnergy -= sent;
   > 75  			needsInvUpdate = sent > 0L;
   > 76  		}
   > 77  		if ((getDemandedEnergy() > 0L) && (!this.mDischargeSlot.isEmpty()))
   > 78  		{
   > 79  			double gain = this.mDischargeSlot.discharge(this.mMaxStorage - this.mEnergy, false);
   > 80
   > 81  			this.mEnergy += gain;
   > 82  			needsInvUpdate = gain > 0L;
   > 83  		}
   > 84  		if ((this.mRedstoneMode == 5) || (this.mRedstoneMode == 6)) {
   > 85  			this.mHasRedstone = this.worldObj.isBlockIndirectlyGettingPowered(this.xCoord, this.yCoord, this.zCoord);
   > 86  		}
   > 87  		boolean shouldEmitRedstone = shouldEmitRedstone();
   > 88  		if (shouldEmitRedstone != this.mIsEmittingRedstone)
   > 89  		{
   > 90  			this.mIsEmittingRedstone = shouldEmitRedstone;
   > 91  			setActive(this.mIsEmittingRedstone);
   > 92
   > 93  			this.worldObj.notifyBlocksOfNeighborChange(this.xCoord, this.yCoord, this.zCoord, this.worldObj.getBlock(this.xCoord, this.yCoord, this.zCoord));
   > 94  		}
   > 95  		if (needsInvUpdate) {
   > 96  			markDirty();
   > 97  		}
   > 98  	}
     99
    100  	public boolean shouldEmitRedstone()
    101  	{
    102  		boolean shouldEmitRedstone = false;
    103  		switch (this.mRedstoneMode)
    104  		{
    105  		case 1:
    106  			shouldEmitRedstone = this.mEnergy >= this.mMaxStorage - this.mOutput * 20;
    107  			break;
    108  		case 2:
   ```

9. `NotEnoughItems (PR 1146)`, `WorldOverlayRenderer.java` (Claude)

   ```java
    119          for (int chunkX = MOB_OVERLAY_SCAN.getMinChunkX(); chunkX <= MOB_OVERLAY_SCAN.getMaxChunkX(); chunkX++) {
    120              for (int chunkZ = MOB_OVERLAY_SCAN.getMinChunkZ(); chunkZ <= MOB_OVERLAY_SCAN.getMaxChunkZ(); chunkZ++) {
    121                  if (!MOB_OVERLAY_LIST.beginChunk(MOB_OVERLAY_SCAN, chunkX, chunkZ)) continue;
    122
    123                  MOB_OVERLAY_LIST.endChunk(compileChunkFaces(style, chunkX, chunkZ));
    124              }
    125          }
    126          MOB_OVERLAY_LIST.endCompile(MOB_OVERLAY_SCAN);
    127      }
    128
   >129      private static boolean compileChunkFaces(MobOverlayStyle style, int chunkX, int chunkZ) {
   >130          final int CHUNK_WIDTH = 1 << MobOverlayScan.CHUNK_SHIFT;
   >131          final float alpha = style.computeAlpha();
   >132          final Tessellator tess = Tessellator.instance;
   >133          final int cornerX = chunkX << MobOverlayScan.CHUNK_SHIFT;
   >134          final int cornerZ = chunkZ << MobOverlayScan.CHUNK_SHIFT;
   >135          final int minX = MOB_OVERLAY_SCAN.getMinX();
   >136          final int minZ = MOB_OVERLAY_SCAN.getMinZ();
   >137          final int span = MOB_OVERLAY_SCAN.getSpan();
   >138          final int height = MOB_OVERLAY_SCAN.getHeight();
   >139          boolean hasFaces = false;
   >140          tess.startDrawing(style.glMode);
   >141          for (int i = Math.max(cornerX - minX, 0); i < Math.min(cornerX + CHUNK_WIDTH - minX, span); i++) {
   >142              for (int j = Math.max(cornerZ - minZ, 0); j < Math.min(cornerZ + CHUNK_WIDTH - minZ, span); j++) {
   >143                  MOB_OVERLAY_SCAN.readColumn(i, j, COLUMN_CELLS);
   >144                  for (int k = 0; k < height; k++) {
   >145                      if (MobOverlayScan.extractSpawnMode(COLUMN_CELLS[k]) == 0) continue;
   >146
   >147                      MARKED_FACE.moveTo(
   >148                              minX + i - cornerX,
   >149                              k + MobOverlayScan.computeOverlayYOffset(COLUMN_CELLS[k]),
   >150                              minZ + j - cornerZ);
   >151                      loadNeighbourModes(i, k, j);
   >152                      MARKED_FACE.applyColor(style.colouring, alpha);
   >153                      style.addVertices(MARKED_FACE);
   >154                      hasFaces = true;
   >155                  }
   >156              }
   >157          }
   >158          tess.draw();
   >159          return hasFaces;
   >160      }
    161
    162      private static void beginMobOverlayDraw(MobOverlayStyle style) {
    163          final ResourceLocation texture = style.texture;
    164          if (texture == null) {
    165              GL11.glDisable(GL11.GL_TEXTURE_2D);
    166          } else {
    167              GL11.glEnable(GL11.GL_TEXTURE_2D);
    168              Minecraft.getMinecraft().getTextureManager().bindTexture(texture);
    169          }
    170          GL11.glEnable(GL11.GL_BLEND);
   ```

10. `Galaxy-Space-GTNH`, `RenderIceBolt.java`

   ```java
     87      protected ResourceLocation getEntityTexture(final EntityIceBolt p_110775_1_) {
     88          return RenderIceBolt.ballTextures;
     89      }
     90
     91      @Override
     92      protected ResourceLocation getEntityTexture(final Entity p_110775_1_) {
     93          return this.getEntityTexture((EntityIceBolt) p_110775_1_);
     94      }
     95
     96      @Override
   > 97      public void doRender(
   > 98              final Entity p_76986_1_,
     99              final double p_76986_2_,
    100              final double p_76986_4_,
    101              final double p_76986_6_,
    102              final float p_76986_8_,
    103              final float p_76986_9_) {
    104          this.doRender((EntityIceBolt) p_76986_1_, p_76986_2_, p_76986_4_, p_76986_6_, p_76986_8_, p_76986_9_);
    105      }
    106
    107      static {
    108          ballTextures = new ResourceLocation("galaxyspace:textures/model/plasmaBall.png");
   ```

11. `CoFHCore`, `CCModelLibrary.java`

   ```java
    69  		addIcosahedronTriangle(verts[3], 0.5, 1, verts[2], 0, 0.75, verts[4], 1, 0.75);
    70  		addIcosahedronTriangle(verts[3], 0.5, 1, verts[7], 0, 0.75, verts[2], 1, 0.75);
    71  		addIcosahedronTriangle(verts[3], 0.5, 1, verts[11], 0, 0.75, verts[7], 1, 0.75);
    72  		addIcosahedronTriangle(verts[3], 0.5, 1, verts[10], 0, 0.75, verts[11], 1, 0.75);
    73  		addIcosahedronTriangle(verts[3], 0.5, 1, verts[4], 0, 0.75, verts[10], 1, 0.75);
    74
    75  		icosahedron4.computeNormals().smoothNormals();
    76  		icosahedron7.computeNormals().smoothNormals();
    77  	}
    78
   >79  	private static void addIcosahedronTriangle(Vector3 vec1, double u1, double v1, Vector3 vec2, double u2, double v2, Vector3 vec3, double u3, double v3) {
   >80
   >81  		icosahedron4.verts[i * 3] = icosahedron7.verts[i * 4] = new Vertex5(vec1, u1, v1);
   >82  		icosahedron4.verts[i * 3 + 1] = icosahedron7.verts[i * 4 + 1] = new Vertex5(vec2, u2, v2);
   >83  		icosahedron4.verts[i * 3 + 2] = icosahedron7.verts[i * 4 + 2] = icosahedron7.verts[i * 4 + 3] = new Vertex5(vec3, u3, v3);
   >84  		i++;
   >85  	}
    86
    87  	public static Matrix4 getRenderMatrix(Vector3 position, Rotation rotation, double scale) {
    88
    89  		return new Matrix4().translate(position).apply(new Scale(scale)).apply(rotation);
    90  	}
    91  }
    92
   ```

12. `CraftGuide`, `ItemSlot.java`

   ```java
    53  	public SlotType slotType = SlotType.INPUT_SLOT;
    54
    55  	/**
    56  	 * Implementation of ItemSlot functionality, allowing it
    57  	 * to change if needed, without altering the API. This
    58  	 * field is set during CraftGuide's {@literal @PreInit}.
    59  	 */
    60  	public static ItemSlotImplementation implementation;
    61
    62  	(javadoc removed)
   >63  	public ItemSlot(int x, int y, int width, int height)
   >64  	{
   >65  		this(x, y, width, height, false);
   >66  	}
    67
    68  	/**
    69  	 * Creates a new ItemSlot
    70  	 * @param x
    71  	 * @param y
    72  	 * @param width
    73  	 * @param height
    74  	 * @param drawQuantity
    75  	 */
    76  	public ItemSlot(int x, int y, int width, int height, boolean drawQuantity)
   ```

13. `CoFHCore`, `BlockFluidInteractive.java`

   ```java
    14  public class BlockFluidInteractive extends BlockFluidCoFHBase implements IBakeable {
    15
    16  	protected final TMap<BlockWrapper, BlockWrapper> collisionMap = new THashMap<BlockWrapper, BlockWrapper>();
    17
    18  	public BlockFluidInteractive(Fluid fluid, Material material, String name) {
    19
    20  		super(fluid, material, name);
    21  		CoFHCore.registerBakeable(this);
    22  	}
    23
   >24  	public BlockFluidInteractive(String modName, Fluid fluid, Material material, String name) {
   >25
   >26  		super(modName, fluid, material, name);
   >27  		CoFHCore.registerBakeable(this);
   >28  	}
    29
    30  	public boolean addInteraction(Block preBlock, Block postBlock) {
    31
    32  		if (preBlock == null || postBlock == null) {
    33  			return false;
    34  		}
    35  		return addInteraction(preBlock, -1, postBlock, 0);
    36  	}
    37
    38  	public boolean addInteraction(Block preBlock, int preMeta, Block postBlock, int postMeta) {
   ```

14. `Prism`, `InventoryListener.java`

   ```java
    238                      .source(event.getCause())
    239                      .event(PrismEvents.ITEM_DROP)
    240                      .itemStack(itemStack)
    241                      .location(player.getLocation())
    242                      .buildAndSave();
    243          }
    244      }
    245
    246      (javadoc removed)
    247      @Listener(order = Order.POST)
   >248      public void onInteractInventory(InteractInventoryEvent event, @Root Player player) {
   >249          if (!(event.getTargetInventory() instanceof CarriedInventory)
   >250                  || (!Prism.getInstance().getConfig().getEventCategory().isInventoryClose() && !Prism.getInstance().getConfig().getEventCategory().isInventoryOpen())) {
   >251              return;
   >252          }
   >253
   >254          CarriedInventory<? extends Carrier> carriedInventory = (CarriedInventory<? extends Carrier>) event.getTargetInventory();
   >255          if (carriedInventory.getCarrier().filter(Player.class::isInstance).isPresent()) {
   >256              return;
   >257          }
   >258
   >259          // Get the location of the inventory otherwise fallback on the players location
   >260          Location<World> location = carriedInventory.getCarrier()
   >261                  .filter(Locatable.class::isInstance)
   >262                  .map(Locatable.class::cast)
   >263                  .map(Locatable::getLocation)
   >264                  .orElse(player.getLocation());
   >265
   >266          // Get the title of the inventory otherwise fallback on the class name
   >267          String title = carriedInventory.getProperty(InventoryTitle.class, InventoryTitle.PROPERTY_NAME)
   >268                  .map(InventoryTitle::getValue)
   >269                  .map(Text::toPlain)
   >270                  .orElse(carriedInventory.getClass().getSimpleName());
   >271
   >272          PrismRecord.EventBuilder eventBuilder = PrismRecord.create()
   >273                  .source(event.getCause())
   >274                  .container(title)
   >275                  .location(location);
   >276
   >277          if (event instanceof InteractInventoryEvent.Close && Prism.getInstance().getConfig().getEventCategory().isInventoryClose()) {
   >278              eventBuilder.event(PrismEvents.INVENTORY_CLOSE).buildAndSave();
   >279          } else if (event instanceof InteractInventoryEvent.Open && Prism.getInstance().getConfig().getEventCategory().isInventoryOpen()) {
   >280              eventBuilder.event(PrismEvents.INVENTORY_OPEN).buildAndSave();
   >281          }
   >282      }
    283  }
   ```

## Q4. `The` and `A` as the first word

Rule 12 bans `The` as the first word of a comment or a docstring. Label each example **G** or **B**.

1. `SpongePoweredMixinUpstream`, `Injector.java`: a later sentence opens with `The`

   ```java
    603          boolean canCoerce = Injector.canCoerce(fromType, toType);
    604          if (!canCoerce) {
    605              throw new InvalidInjectionException(this.info, String.format(
    606                      "%s has an invalid signature. Cannot @Coerce %s type %s%s to %s", description, argType,
    607                      SignaturePrinter.getTypeName(toType), argIndex, SignaturePrinter.getTypeName(fromType)));
    608          }
    609
    610          return true;
    611      }
    612
   >613      /**
   >614       * Throw an exception. The exception class must have a string which takes a
   >615       * string argument
   >616       *
   >617       * @param insns Insn list to inject into
   >618       * @param exceptionType Type of exception to throw (binary name)
   >619       * @param message Message to pass to the exception constructor
   >620       */
    621      protected void throwException(InsnList insns, String exceptionType, String message) {
    622          insns.add(new TypeInsnNode(Opcodes.NEW, exceptionType));
    623          insns.add(new InsnNode(Opcodes.DUP));
    624          insns.add(new LdcInsnNode(message));
    625          insns.add(new MethodInsnNode(Opcodes.INVOKESPECIAL, exceptionType, "<init>", "(Ljava/lang/String;)V", false));
    626          insns.add(new InsnNode(Opcodes.ATHROW));
    627      }
    628
    629      /**
    630       * Returns whether the <tt>from</tt> type can be coerced to the <tt>to</tt>
   ```

2. `SpecialSource`, `Jar.java`: a later sentence opens with `The`

   ```java
    215       * Read a new jar instance from the given file.
    216       *
    217       * @param file
    218       * @return
    219       * @throws IOException
    220       */
    221      public static Jar init(File file) throws IOException {
    222          return init(Collections.singletonList(file));
    223      }
    224
   >225      /**
   >226       * Read a new jar instance from the given list of files.
   >227       *
   >228       * @param files
   >229       * @return
   >230       * @throws IOException
   >231       */
   >232      public static Jar init(List<File> files) throws IOException {
   >233          Preconditions.checkArgument(files.size() > 0, "Jar init requires at least one file!");
   >234
   >235          // Save some time by resizing these to their target size
   >236          List<JarFile> jarFiles = new ArrayList<JarFile>(files.size());
   >237          List<String> filenames = new ArrayList<String>(files.size());
   >238
   >239          // Populate file names and JarFiles
   >240          for (File file : files) {
   >241              filenames.add(file.getName());
   >242              jarFiles.add(new JarFile(file, false));
   >243          }
   >244
   >245          LinkedHashMap<String, JarFile> jarForResource = collectJarFiles(jarFiles);
   >246          String fileName = Joiner.on(" + ").join(filenames);
   >247
   >248          String main = null;
   >249          // For each jar
   >250          for (JarFile jar : jarFiles) {
   >251              // Get main
   >252              String newMain = getMainClassName(jar.getManifest());
   >253              // If they have a main
   >254              if (newMain != null) {
   >255                  // If we haven't set a main already, then set
   >256                  if (main == null) {
   >257                      main = newMain;
   >258                  } else {
   >259                      // Else warn that there are many main classes in the set we have been given
   >260                      System.err.println("[Warning] Duplicate Main classes for " + fileName);
   >261                  }
   >262              }
   >263          }
   >264
   >265          // Return the new all encompassing jar instance. The file name will be the sum of all names.
   >266          return new Jar(jarFiles, main, fileName, jarForResource);
   >267      }
   >268
   >269      /**
   >270       * Closes all jar files in this Jar
   >271       *
   >272       * @see java.io.Closeable
   >273       * @throws IOException if an I/O error has occurred
   >274       */
    275      @Override
    276      public void close() throws IOException {
    277          for (JarFile jarFile : jarFiles) {
    278              jarFile.close();
    279          }
    280          jarFiles.clear();
    281          jarForResource.clear();
    282          contains.clear();
    283      }
    284  }
   ```

3. `SpongePoweredMixinUpstream`, `InjectionPoint.java`: a later sentence opens with `The`

   ```java
    774          }
    775
    776          throw new InvalidInjectionException(context, message);
    777      }
    778
    779      protected String getAtCode() {
    780          AtCode code = this.getClass().<AtCode>getAnnotation(AtCode.class);
    781          return code == null ? this.getClass().getName() : code.value();
    782      }
    783
   >784      /**
   >785       * Register an injection point class. The supplied class must be decorated
   >786       * with an {@link AtCode} annotation for registration purposes.
   >787       *
   >788       * @param type injection point type to register
   >789       */
    790      public static void register(Class<? extends InjectionPoint> type) {
    791          AtCode code = type.<AtCode>getAnnotation(AtCode.class);
    792          if (code == null) {
    793              throw new IllegalArgumentException("Injection point class " + type + " is not annotated with @AtCode");
    794          }
    795
    796          Class<? extends InjectionPoint> existing = InjectionPoint.types.get(code.value());
    797          if (existing != null && !existing.equals(type)) {
    798              LogManager.getLogger("mixin").debug("Overriding InjectionPoint {} with {} (previously {})", code.value(), type.getName(),
    799                      existing.getName());
   ```

4. `NotEnoughProduction`, `CustomScrollPane.java`: a later sentence opens with `The`

   ```java
    921  	/** Returns true if the widget is larger than the scroll pane horizontally. */
    922  	public boolean isScrollX () {
    923  		return scrollX;
    924  	}
    925
    926  	/** Returns true if the widget is larger than the scroll pane vertically. */
    927  	public boolean isScrollY () {
    928  		return scrollY;
    929  	}
    930
   >931  	/** Disables scrolling in a direction. The widget will be sized to the FlickScrollPane in the disabled direction. */
    932  	public void setScrollingDisabled (boolean x, boolean y) {
    933  		disableX = x;
    934  		disableY = y;
    935  		invalidate();
    936  	}
    937
    938  	public boolean isScrollingDisabledX () {
    939  		return disableX;
    940  	}
    941
   ```

5. `SpongePoweredMixinUpstream`, `SourceMap.java`: a field javadoc opens with `The`

   ```java
    51           * File index in stratum
    52           */
    53          public final int id;
    54
    55          /**
    56           * The base line offset for this stratum, line numbers in the output
    57           * will be offset by this amount from their originals
    58           */
    59          public final int lineOffset;
    60
   >61          /**
   >62           * The size of this stratum (number of lines)
   >63           */
    64          public final int size;
    65
    66          /**
    67           * Actual source file name to include in the smap
    68           */
    69          public final String sourceFileName;
    70
    71          /**
    72           * Full path to the source file
    73           */
   ```

6. `SpongePoweredMixinUpstream`, `InjectionInfo.java`: a field javadoc opens with `The`

   ```java
    186      /**
    187       * Target method(s)
    188       */
    189      protected final Deque<MethodNode> targets = new ArrayDeque<MethodNode>();
    190
    191      /**
    192       * Method slice descriptors parsed from the annotation
    193       */
    194      protected final MethodSlices slices;
    195
   >196      /**
   >197       * The key into the annotation which contains the injection points
   >198       */
    199      protected final String atKey;
    200
    201      /**
    202       * Injection points parsed from
    203       * {@link org.spongepowered.asm.mixin.injection.At} annotations
    204       */
    205      protected final List<InjectionPoint> injectionPoints = new ArrayList<InjectionPoint>();
    206
    207      /**
    208       * Map of lists of nodes enumerated by calling {@link #prepare}
   ```

7. `GT5-Unofficial-tooltips`, `GT_GUICover.java`: a field javadoc opens with `The`

   ```java
    18      }
    19
    20      @Override
    21      public void updateScreen() {
    22          super.updateScreen();
    23          if (!tile.isUseableByPlayer(mc.thePlayer)) {
    24              closeScreen();
    25          }
    26      }
    27
   >28      /**
   >29       * The parent GUI to exit to. -1 is ignored.
   >30       * @param parentGuiId
   >31       */
    32      public void setParentGuiId(int parentGuiId) {
    33          this.parentGuiId = parentGuiId;
    34      }
    35
    36      @Override
    37      public void closeScreen() {
    38          // If this cover was given a guiId, tell the server to open it for us when this GUI closes.
    39          if (parentGuiId != -1 && tile.isUseableByPlayer(mc.thePlayer)) {
    40              GT_Values.NW.sendToServer(new GT_Packet_GtTileEntityGuiRequest(
    41                      tile.getXCoord(),
   ```

8. `NotEnoughProduction`, `CustomScrollPane.java`: a field javadoc opens with `The`

   ```java
    1092  	public void drawDebug (ShapeRenderer shapes) {
    1093  		shapes.flush();
    1094  		applyTransform(shapes, computeTransform());
    1095  		if (ScissorStack.pushScissors(scissorBounds)) {
    1096  			drawDebugChildren(shapes);
    1097  			ScissorStack.popScissors();
    1098  		}
    1099  		resetTransform(shapes);
    1100  	}
    1101
   >1102  	/** The style for a scroll pane, see {@link ScrollPane}.
   >1103  	 * @author mzechner
   >1104  	 * @author Nathan Sweet */
    1105  	static public class ScrollPaneStyle {
    1106  		/** Optional. */
    1107  		public Drawable background, corner;
    1108  		/** Optional. */
    1109  		public Drawable hScroll, hScrollKnob;
    1110  		/** Optional. */
    1111  		public Drawable vScroll, vScrollKnob;
    1112
    1113  		public ScrollPaneStyle () {
    1114  		}
   ```

9. `SpecialSource`, `Pair.java`: a class javadoc opens with `A`

   ```java
    25   * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
    26   * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
    27   * POSSIBILITY OF SUCH DAMAGE.
    28   */
    29  package net.md_5.specialsource.util;
    30
    31  import lombok.EqualsAndHashCode;
    32  import lombok.RequiredArgsConstructor;
    33  import lombok.ToString;
    34
   >35  /**
   >36   * A class representing a set of 2 objects as defined by the type parameters.
   >37   *
   >38   * @param <E> type of element
   >39   */
    40  @ToString
    41  @EqualsAndHashCode
    42  @RequiredArgsConstructor
    43  public class Pair<E> {
    44
    45      public final E first;
    46      public final E second;
    47  }
    48
   ```

10. `SpongePoweredMixinUpstream`, `MixinContainer.java`: a class javadoc opens with `A`

   ```java
    29  import java.util.Iterator;
    30  import java.util.List;
    31
    32  import org.apache.logging.log4j.LogManager;
    33  import org.apache.logging.log4j.Logger;
    34  import org.spongepowered.asm.launch.GlobalProperties;
    35  import org.spongepowered.asm.launch.platform.IMixinPlatformAgent.AcceptResult;
    36  import org.spongepowered.asm.launch.platform.container.IContainerHandle;
    37  import org.spongepowered.asm.service.MixinService;
    38
   >39  /**
   >40   * A collection of {@link IMixinPlatformAgent} platform agents) for a particular
   >41   * container
   >42   */
    43  public class MixinContainer {
    44
    45      private static final List<String> agentClasses = new ArrayList<String>();
    46
    47      static {
    48          GlobalProperties.put(GlobalProperties.Keys.AGENTS, MixinContainer.agentClasses);
    49          for (String agent : MixinService.getService().getPlatformAgents()) {
    50              MixinContainer.agentClasses.add(agent);
    51          }
    52          MixinContainer.agentClasses.add("org.spongepowered.asm.launch.platform.MixinPlatformAgentDefault");
   ```

11. `GT5-Unofficial`, `IDigitalChest.java`: a class javadoc opens with `A`

   ```java
    12       * Do not assume that it's a Digital Chest or similar Device, when it just implements this Interface.
    13       */
    14      boolean isDigitalChest();
    15
    16      /**
    17       * Gives an Array of Stacks with Size (of all the Data-stored Items) of the correspondent Item kinds (regular QChests have only one)
    18       * Does NOT include the 64 "ready" Items inside the Slots, and neither the 128 Items in the overflow Buffer.
    19       */
    20      ItemStack[] getStoredItemData();
    21
   >22      /**
   >23       * A generic Interface for just setting the amount of contained Items
   >24       */
    25      void setItemCount(int aCount);
    26
    27      /**
    28       * Gets the maximum Item count for this QChest alike Storage. This applies to the Data-Storage, not for the up to 192 buffered Items!
    29       */
    30      int getMaxItemCount();
    31  }
    32
   ```

12. `MobOverlayStyle.java` (Claude, NEI PR 1146, inbox pub 25): a class javadoc opens with `A`

   ```java
     2
     3  import java.util.Locale;
     4  import java.util.StringJoiner;
     5
     6  import javax.annotation.Nullable;
     7
     8  import net.minecraft.util.ResourceLocation;
     9
    10  import org.lwjgl.opengl.GL11;
    11
   >12  /** A mark of the mob spawn overlay. {@code world.overlays.mobOverlayStyle} is saved as {@link #formatName()}. */
    13  public enum MobOverlayStyle {
    14
    15      /** NEI's original cross from corner to corner. */
    16      X(GL11.GL_LINES) {
    17
    18          @Override
    19          public void addVertices(MobOverlayFace face) {
    20              face.addVertex(0, 0);
    21              face.addVertex(1, 1);
    22              face.addVertex(1, 0);
   ```

13. `MobOverlayDisplayList.java` (Claude, NEI PR 1146, inbox pub 26): a class javadoc opens with `A`

   ```java
     1  package codechicken.nei;
     2
     3  import net.minecraft.client.renderer.GLAllocation;
     4
     5  import org.lwjgl.opengl.GL11;
     6
   > 7  /** A GL display list of the mob spawn overlay. */
     8  public final class MobOverlayDisplayList {
     9
    10      private int listId = -1;
    11      private int modesVersion;
    12      private MobOverlayStyle style;
    13
    14      public boolean isCompiled(int currentModesVersion, MobOverlayStyle currentStyle) {
    15          return listId >= 0 && modesVersion == currentModesVersion && style == currentStyle;
    16      }
    17
   ```

## Q5. Openers with a platform

Rule 6 asks for a condition as a clause after `when` or `if`. Label each example **G** or **B**.

1. `concurrent/futures/process.py:121`

   ```python
    111  # See bpo-39812 for context.
    112  threading._register_atexit(_python_exit)
    113
    114  # Controls how many more calls than processes will be queued in the call queue.
    115  # A smaller number will mean that processes spend more time idle waiting for
    116  # work while a larger number will make Future.cancel() succeed less frequently
    117  # (Futures in the call queue cannot be cancelled).
    118  EXTRA_QUEUED_CALLS = 1
    119
    120
   >121  # On Windows, WaitForMultipleObjects is used to wait for processes to finish.
   >122  # It can wait on, at most, 63 objects. There is an overhead of two objects:
   >123  # - the result queue reader
   >124  # - the thread wakeup reader
    125  _MAX_WINDOWS_WORKERS = 63 - 2
    126
    127  # Hack to embed stringification of remote traceback in local traceback
    128
    129  class _RemoteTraceback(Exception):
    130      def __init__(self, tb):
    131          self.tb = tb
    132      def __str__(self):
    133          return self.tb
    134
   ```

2. `zipimport.py:467`

   ```python
    457                  comment_size = _unpack_uint16(buffer[32:34])
    458                  file_offset = _unpack_uint32(buffer[42:46])
    459                  header_size = name_size + extra_size + comment_size
    460
    461                  try:
    462                      name = fp.read(name_size)
    463                  except OSError:
    464                      raise ZipImportError(f"can't read Zip file: {archive!r}", path=archive)
    465                  if len(name) != name_size:
    466                      raise ZipImportError(f"can't read Zip file: {archive!r}", path=archive)
   >467                  # On Windows, calling fseek to skip over the fields we don't use is
   >468                  # slower than reading the data because fseek flushes stdio's
   >469                  # internal buffers.    See issue #8745.
    470                  try:
    471                      extra_data_len = header_size - name_size
    472                      extra_data = memoryview(fp.read(extra_data_len))
    473
    474                      if len(extra_data) != extra_data_len:
    475                          raise ZipImportError(f"can't read Zip file: {archive!r}", path=archive)
    476                  except OSError:
    477                      raise ZipImportError(f"can't read Zip file: {archive!r}", path=archive)
    478
    479                  if flags & 0x800:
   ```

3. `test/support/socket_helper.py:178`

   ```python
    168          return test
    169
    170
    171  def get_socket_conn_refused_errs():
    172      """
    173      Get the different socket error numbers ('errno') which can be received
    174      when a connection is refused.
    175      """
    176      errors = [errno.ECONNREFUSED]
    177      if hasattr(errno, 'ENETUNREACH'):
   >178          # On Solaris, ENETUNREACH is returned sometimes instead of ECONNREFUSED
    179          errors.append(errno.ENETUNREACH)
    180      if hasattr(errno, 'EADDRNOTAVAIL'):
    181          # bpo-31910: socket.create_connection() fails randomly
    182          # with EADDRNOTAVAIL on Travis CI
    183          errors.append(errno.EADDRNOTAVAIL)
    184      if hasattr(errno, 'EHOSTUNREACH'):
    185          # bpo-37583: The destination host cannot be reached
    186          errors.append(errno.EHOSTUNREACH)
    187      if not IPV6_ENABLED:
    188          errors.append(errno.EAFNOSUPPORT)
   ```

4. `subprocess.py:997`

   ```python
     987
     988          # Input and output objects. The general principle is like
     989          # this:
     990          #
     991          # Parent                   Child
     992          # ------                   -----
     993          # p2cwrite   ---stdin--->  p2cread
     994          # c2pread    <--stdout---  c2pwrite
     995          # errread    <--stderr---  errwrite
     996          #
   > 997          # On POSIX, the child objects are file descriptors.  On
   > 998          # Windows, these are Windows file handles.  The parent objects
   > 999          # are file descriptors on both platforms.  The parent objects
   >1000          # are -1 when not using PIPEs. The child objects are -1
   >1001          # when not redirecting.
    1002
    1003          (p2cread, p2cwrite,
    1004           c2pread, c2pwrite,
    1005           errread, errwrite) = self._get_handles(stdin, stdout, stderr)
    1006
    1007          # From here on, raising exceptions may cause file descriptor leakage
    1008
    1009          # We wrap OS handles *before* launching the child, otherwise a
    1010          # quickly terminating child could make our fds unwrappable
    1011          # (see #8458).
   ```

5. `MilestoneFile.java` (Claude, inbox pub 10, flagged by you)

   ```java
     4
     5      public static final String FILE_NAME = "gtnhspeedrunlivesplit-milestones.json";
     6      // the splits file of protocol 2 and older
     7      private static final String OLD_FILE_NAME = "gtnhspeedrunlivesplit-splits.json";
     8      private static final String SAMPLE_RESOURCE = "/assets/gtnhspeedrunlivesplit/sample-milestones.json";
     9      private static final String DEFAULT_GAME_NAME = "GregTech: New Horizons";
    10      private static final String DEFAULT_CATEGORY = "Any%";
    11
    12      private MilestoneFile() {}
    13
   >14      /**
   >15       * Read the milestone file in {@code configDir}. A missing file is created from the sample.
   >16       * Beside the splits file of an older version, no file is created, and the {@link SplitFileException} has the
   >17       * steps to move the splits.
   >18       */
    19      public static MilestoneRules readOrCreate(Path configDir) throws SplitFileException {
    20          final Path rulesPath = configDir.resolve(FILE_NAME);
    21          if (!Files.exists(rulesPath)) {
    22              final Path oldPath = configDir.resolve(OLD_FILE_NAME);
    23              if (Files.exists(oldPath)) {
    24                  throw new SplitFileException(
    25                      oldPath + " is the splits file of an older version. Move the file's splits into \"milestones\" of "
    26                          + rulesPath
    27                          + ", each with an \"id\", then delete the old file (expected the format in the README)");
    28              }
   ```

