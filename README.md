# MP3プレイヤー MCPサーバー

指定フォルダー内のMP3ファイルを再生・停止・一覧取得できるMCPサーバーです。

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

### 4. Claude Desktop の設定

#### Macの場合：
`~/Library/Application Support/Claude/claude_desktop_config.json` を編集

#### Windowsの場合：
`%APPDATA%\Claude\claude_desktop_config.json` を編集

設定例：

```json
{
  "mcpServers": {
    "mp3-player": {
      "command": "python3",
      "args": [
        "/Users/yourname/Documents/mcp-servers/mp3_player_server.py"
      ],
      "env": {
        "MUSIC_FOLDER": "/Users/yourname/Music/MyMP3s"
      }
    }
  }
}
```

**重要：**
- `args` の部分を `mp3_player_server.py` の実際のパスに変更してください
- `MUSIC_FOLDER` をMP3ファイルが入っているフォルダーのパスに変更してください

### 5. Claude Desktop の再起動

設定を反映させるため、Claude Desktop アプリを完全に終了して再起動します。

## 使い方

Claude と会話する際、以下のようなリクエストができます：

### MP3ファイル一覧を取得
```
音楽フォルダーにあるMP3ファイルを教えて
```

### MP3ファイルを再生
```
"song.mp3" を再生して
```

### 再生を停止
```
音楽を停止して
```

### 再生状態を確認
```
今何が再生されているか教えて
```

## 利用可能なツール

1. **list_mp3_files**: 音楽フォルダー内の全MP3ファイルをリスト表示
2. **play_mp3**: 指定したMP3ファイルを再生
3. **stop_playback**: 現在の再生を停止
4. **get_playback_status**: 再生状態を取得

## トラブルシューティング

### MCPサーバーが認識されない場合

1. Claude Desktop を完全に終了（タスクトレイからも）
2. 設定ファイルのJSONが正しいか確認（カンマ、括弧など）
3. ファイルパスが正しいか確認
4. Claude Desktop のログを確認
   - Mac: `~/Library/Logs/Claude/`
   - Windows: `%APPDATA%\Claude\logs\`

### 音楽が再生されない場合

1. MUSIC_FOLDERのパスが正しいか確認
2. フォルダー内に.mp3ファイルが存在するか確認
3. ファイル名に日本語や特殊文字が含まれている場合、エンコーディングの問題が起こる可能性があります

### pygameのエラーが出る場合

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

## ライセンス

MIT License
