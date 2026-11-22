# Rule 11 on `MobOverlayScan.java`: before and after

The file is `src/main/java/codechicken/nei/moboverlay/MobOverlayScan.java` of NEI, branch `mob-overlay-perf`, commit
177b37f. The file has 15 javadocs. After rule 11 and rule 15, 7 javadocs stay, and one of the 7 is reworded.

The questions, by rule 11 and rule 15:

- a method of one line: no javadoc (rule 15)
- a method over 20 body lines without a javadoc: can a reader learn from the name of the method and the comments of
  the body what the method does? If not, write a javadoc
- a method with a javadoc: what does a reader learn from the javadoc, and not from the name of the method or the
  comments of the body? If nothing, cut the javadoc
- a class: keep the javadoc of the top-level type (`NAR118`). Give a nested class a javadoc only for a fact that a
  reader can't get from the name and the code (J1-F07)

The demo changes only whether a javadoc stays. Under other rules of round 12, I would reword some of the 7, such as
the first sentence of the class javadoc under rule 12. The demo leaves those changes out.

## Cut: 8 javadocs

| line | member | javadoc | reason |
|---|---|---|---|
| 123 | `getModesVersion()`, 1 line | `The version changes when a spawn mode or the top of a flat block changes, or the box moves.` | rule 15 |
| 168 | `readChunkVersion()`, 1 line | `The version changes when a cell in or beside the chunk column changes, and when the box moves.` | rule 15 |
| 173 | `readSpawnMode()`, 1 line | `{@code i} and {@code j} are from 0 to {@link #getSpan}, and {@code k} is from 0 to {@link #getHeight}.` | rule 15 |
| 235 | `moveBox()`, 39 lines | `@return whether the box moved` | the name and the `boolean` give the same fact |
| 304 | `scanColumn()`, 3 lines | `@return whether a spawn mode or the top of a flat block changed` | the same text is on `Column.scan()`, which `scanColumn()` returns |
| 370 | nested class `Column` | `{@link #moveTo} reads a column's chunk, biome and highest non-air block in the box, and {@link #scan} reads the column's blocks.` | a reader gets the same from the bodies of `moveTo()` and `scan()` |
| 414 | `getSpawnMode()`, 25 lines | `The spawn mode of the block at height {@code y} in this column.` | a reader gets the same fact from the name and the signature. Each step is in a comment of the body, and the values 0, 1 and 2 are in the class javadoc |
| 462 | nested class `ChangeListener` | `Marks the columns of the block and light changes in {@link #scannedWorld}.` | a reader gets the same from the name, `IWorldAccess` and `markChanged()` |

The 3 cuts by rule 15 lose facts for a caller: what changes a version, and the range of `i`, `j` and `k`. You ruled on
2026-11-21 that a one-line function gets no javadoc, even over a fact like that.

## Reworded: 1 javadoc

`update()`, line 88, 24 body lines. From the name, a reader learns when the method runs, and not what the method does.
The current javadoc has the cases of a full scan and the clamp of the radii. Both are in the body: the condition before
`scanFullBox()`, and the two calls of `MathHelper.clip()`. The javadoc has nothing on a normal tick.

Before:

```java
    /**
     * Scan every column in this call after {@link #clear}, a change of either radius, a world change, or a move of
     * {@link #getSpan} blocks or more across or {@link #getHeight} blocks or more up or down. {@code newRadius} is
     * clamped between {@link #MIN_RADIUS} and {@link #MAX_RADIUS}, and {@code newVerticalRadius} between
     * {@link #MIN_VERTICAL_RADIUS} and {@link #MAX_VERTICAL_RADIUS}.
     */
    public void update(Entity entity, int newRadius, int newVerticalRadius) {
```

After:

```java
    /** Bring the spawn modes of the box around {@code entity} up to date, at most once per tick. */
    public void update(Entity entity, int newRadius, int newVerticalRadius) {
```

## Kept: 6 javadocs

| line | member | why it stays |
|---|---|---|
| 20 | class `MobOverlayScan` | a top-level type (`NAR118`) |
| 178 | `readColumn()`, 4 lines | the order of the cells, from the bottom of the box to the top. The two `arraycopy()` calls on a ring buffer don't show the order plainly |
| 192 | `computeOverlayYOffset()`, 2 lines | the reason for the offset: a flat block such as a carpet would cover the overlay |
| 324 | `markMovedEdgeChunks()`, 11 lines | the reason for the method: the box has no outline at the edge, so a move changes the outline of the edge cells |
| 401 | `Column.scan()`, 9 lines | the meaning of the `boolean`, now in one place |
| 447 | `readCoverTop()`, 7 lines | the unit of the result, fractions of a block over `COVER_TOP_STEPS`, and 0 for a tall block |

## Methods over 20 body lines without a javadoc

After the cuts, `moveBox()` (39 lines) and `getSpawnMode()` (25 lines) are the methods over 20 body lines without a
javadoc. From the name and the body of `moveBox()`, a reader learns what the method does: `moveBox()` moves the box by
the offset of the centre, and scans the columns that enter the box. From the name and the comments of
`getSpawnMode()`, a reader learns each step. So neither method gets a javadoc.
