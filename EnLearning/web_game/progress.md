Original prompt: "1.加一个排行榜功能 和 总统计功能 2.战棋的元素更丰富一点 3.加一个页面，可以浏览选中目录的 渲染后的words.md和phrases.md"

- Added leaderboard + stats API and UI panels.
- Added book preview page `/book/{id}` rendering words + phrases tables.
- Expanded map to tactical grid with tile types, neighbor moves, tile effects.
- Added render_game_to_text and advanceTime hooks for test automation.

TODOs:
- Run Playwright test loop and inspect screenshots/text state.
- Validate map interactions for 20/30 steps (ensure no dead-ends).
- Check leaderboard/stats display for empty datasets.
