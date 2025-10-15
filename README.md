# MP3プレイヤー MCPサーバー

指定フォルダー内のMP3ファイルを再生・停止・一覧取得できるMCPサーバーです。

## 主な機能

- 🎵 MP3ファイルの再生・停止
- 📋 プレイリスト機能（全曲再生）
- 🎲 シャッフル再生
- 🔄 自動再生（曲が終わったら次の曲へ）
- ⏭️ 次の曲へスキップ
- ⏮️ 前の曲へ戻る
- 🔁 リピートモード（全曲リピート、1曲リピート）

## セットアップ手順

### 1. 必要なライブラリのインストール

```bash
pip install mcp pygame --break-system-packages
```

### 2. ファイルの配置

`mp3_player_server.py` を任意の場所に保存します。
例：`~/Documents/mcp-servers/mp3_player_server.py`

### 3. 実行権限の付与（必要に応じて）

```bash
chmod +x ~/Documents/mcp-servers/mp3_player_server.py
```

### 4. MCP設定

#### Cursor の場合（推奨）：

`~/.cursor/mcp.json` を編集

```json
{
  "mcpServers": {
    "mp3-player": {
      "command": "python3",
      "args": [
        "/Users/yourname/workspace/mp3_player_server/mp3_player_server/mp3_player_server.py"
      ],
      "env": {
        "MUSIC_FOLDER": "/Users/yourname/Music"
      }
    }
  }
}
```

#### Claude Desktop の場合：

**設定ファイルの場所：**
- Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**設定例（pyenvを使用している場合）：**

```json
{
  "mcpServers": {
    "mp3-player": {
      "command": "/Users/yourname/.pyenv/versions/3.11.4/bin/python3",
      "args": [
        "/Users/yourname/workspace/mp3_player_server/mp3_player_server/mp3_player_server.py"
      ],
      "env": {
        "MUSIC_FOLDER": "/Users/yourname/Music"
      }
    }
  }
}
```

**⚠️ 重要な注意点：**

- `args` の部分を `mp3_player_server.py` の実際のパスに変更してください
- `MUSIC_FOLDER` をMP3ファイルが入っているフォルダーのパスに変更してください
- **pyenvを使用している場合**: Claude Desktopは`python3`コマンドでシステムのPythonを使おうとするため、pygameがインストールされていない可能性があります。その場合は、`command`にpyenvの完全なパスを指定してください（例: `/Users/yourname/.pyenv/versions/3.11.4/bin/python3`）
  - 自分のpyenv Pythonパスを確認: `which python3`

### 5. 再起動

設定を反映させるため、以下のいずれかを実行します：
- **Cursor**: Cursorを完全に終了して再起動
- **Claude Desktop**: アプリを完全に終了（タスクトレイからも）して再起動

## 使い方

Claude/Cursor と会話する際、以下のようなリクエストができます：

### 基本操作

#### MP3ファイル一覧を取得
```
音楽フォルダーにあるMP3ファイルを教えて
```

#### MP3ファイルを再生
```
"song.mp3" を再生して
```

#### 全曲を順番に再生
```
全部の曲を再生して
```

#### シャッフル再生
```
全部の曲をシャッフルして再生して
```

#### 再生を停止
```
音楽を停止して
```

#### 再生状態を確認
```
今何が再生されているか教えて
```

### プレイリスト操作

#### 次の曲へスキップ
```
次の曲にして
```

#### 前の曲へ戻る
```
前の曲に戻して
```

### 再生モード設定

#### 順番再生モード
```
順番再生モードにして
```

#### シャッフルモード
```
シャッフルモードにして
```

#### 全曲リピートモード
```
全曲リピートにして
```

#### 1曲リピートモード
```
1曲リピートにして
```

## 利用可能なツール

### 基本ツール
1. **list_mp3_files**: 音楽フォルダー内の全MP3ファイルをリスト表示
2. **play_mp3**: 指定したMP3ファイルを再生
3. **stop_playback**: 現在の再生を停止
4. **get_playback_status**: 再生状態を取得（プレイリスト情報含む）

### プレイリストツール
5. **play_all**: 全曲を再生（シャッフルオプション付き）
6. **next_track**: 次の曲へスキップ
7. **previous_track**: 前の曲へ戻る
8. **set_play_mode**: 再生モードを設定
   - `sequential`: 順番再生
   - `shuffle`: シャッフル再生
   - `repeat_all`: 全曲リピート
   - `repeat_one`: 1曲リピート

### 自動再生機能
曲が終わると、設定されている再生モードに従って自動的に次の曲が再生されます。

## プロジェクト構成

```
mp3_player_server/
├── mp3_player_server.py      # メインサーバー（MCPプロトコル実装）
├── README.md                  # このファイル
└── claude_desktop_config.json # 設定ファイルの例（参考用）
```

## トラブルシューティング

### MCPサーバーが認識されない場合

1. Cursor/Claude Desktop を完全に終了（タスクトレイからも）
2. 設定ファイルのJSONが正しいか確認（カンマ、括弧など）
3. ファイルパスが正しいか確認
4. ログを確認
   - Cursor: DevToolsのコンソール
   - Claude Desktop: `~/Library/Logs/Claude/` (Mac) / `%APPDATA%\Claude\logs\` (Windows)

### "ModuleNotFoundError: No module named 'pygame'" エラーが出る場合

**原因**: Claude Desktopが異なるPythonインタープリターを使用している

**解決方法**:

1. pygameがインストールされているPythonのパスを確認:
   ```bash
   which python3
   # 例: /Users/yourname/.pyenv/shims/python3
   
   python3 -c "import sys; print(sys.executable)"
   # 例: /Users/yourname/.pyenv/versions/3.11.4/bin/python3
   ```

2. Claude Desktopの設定ファイルで、`command`を完全なパスに変更:
   ```json
   "command": "/Users/yourname/.pyenv/versions/3.11.4/bin/python3"
   ```

3. Claude Desktopを再起動

### 音楽が再生されない場合

1. MUSIC_FOLDERのパスが正しいか確認
2. フォルダー内に.mp3ファイルが存在するか確認
3. ファイル名に日本語や特殊文字が含まれている場合、エンコーディングの問題が起こる可能性があります

### pygameのシステム依存関係が不足している場合

```bash
# システムの依存関係をインストール（Ubuntu/Debianの場合）
sudo apt-get install python3-pygame

# macOSの場合
brew install sdl2 sdl2_mixer
```

## カスタマイズ

### 対応形式の追加

コード内の `*.mp3` を他の形式にも対応させることができます：

```python
def get_mp3_files() -> list[str]:
    audio_files = []
    for pattern in ["*.mp3", "*.wav", "*.ogg"]:
        for file in MUSIC_FOLDER.glob(pattern):
            audio_files.append(file.name)
    return sorted(audio_files)
```

### サブフォルダーの検索

```python
def get_mp3_files() -> list[str]:
    mp3_files = []
    for file in MUSIC_FOLDER.rglob("*.mp3"):  # rglob で再帰的に検索
        mp3_files.append(str(file.relative_to(MUSIC_FOLDER)))
    return sorted(mp3_files)
```

## 使用例

### シナリオ1: BGMとして全曲をシャッフル再生
```
ユーザー: 全部の曲をシャッフルして再生して
AI: 🎲 シャッフル再生を開始しました！
```

### シナリオ2: 作業用に全曲をリピート再生
```
ユーザー: 全曲リピートモードにして
AI: 🔁 全曲リピートモードに設定しました
ユーザー: 全部の曲を再生して
AI: 🎵 再生を開始しました（曲が終わると自動で次へ）
```

### シナリオ3: 特定の曲を再生してコントロール
```
ユーザー: かぐや姫を再生して
AI: 🎵 再生開始
ユーザー: 次の曲にして
AI: ⏭️ 次の曲にスキップしました
```

## 技術仕様

- **言語**: Python 3.11+
- **依存関係**: mcp, pygame
- **対応フォーマット**: MP3
- **プロトコル**: MCP (Model Context Protocol)
- **通信方式**: stdio (標準入出力)
- **自動再生**: 非同期タスクで監視
- **日本語対応**: ファイル名に日本語や絵文字を含むファイルに対応

## 既知の問題と制限事項

### 制限事項
- **対応フォーマット**: 現在はMP3ファイルのみ対応（WAV、OGGなどは未対応）
- **サブフォルダー**: デフォルトでは指定フォルダー直下のMP3ファイルのみを検索（サブフォルダーは検索しない）
- **同時再生**: 同時に複数の曲を再生することはできません
- **音量調整**: 現在のバージョンでは音量調整機能はありません
- **プレイリスト保存**: プレイリストの保存機能はありません（セッション終了時にリセット）

### 既知の問題
- **pyenvとClaude Desktop**: Claude Desktopでpyenvを使用している場合、明示的なPythonパスの指定が必要（上記トラブルシューティング参照）
- **長いファイル名**: 極端に長いファイル名（255文字以上）は表示が崩れる可能性があります
- **特殊な文字**: 一部の特殊文字（絵文字以外）を含むファイル名で問題が発生する可能性があります

### 将来の機能追加候補
- 音量調整機能
- WAV、OGG、FLACなどの他のオーディオフォーマット対応
- プレイリストの保存・読込機能
- イコライザー機能
- 再生位置のシーク機能

## ライセンス

MIT License
