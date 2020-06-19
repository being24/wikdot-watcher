# wikdot-watcher

SCPJP用のリストページモジュール用のタグ準拠の監視ツール
特定のタグ付き記事(250以下前提)について監視します

googleAPIのjsonは自分でがんばれ

## SB3用のコード

``` html
[[module ListPages tags="+_contest +_criticism-in" order="updated_at desc" perPage="100"]]
> +++++ [[span class="lp_title"]]%%title_linked%%[[/span]] ( [[span class="lp_fullname"]]/%%fullname%%[[/span]] )
> Created By: [[span class="lp_created_by"]]%%created_by_linked%%[[/span]] / At: [[span class="lp_created_at"]]%%created_at%%[[/span]]
> Updated By: [[span class="lp_updated_by"]]%%updated_by_linked%%[[/span]] / At: [[span class="lp_updated_at"]]%%updated_at%%[[/span]] / Current Rev: [[span class="lp_rev"]]%%revisions%%[[/span]]
> Commented By: [[span class="lp_commented_by"]]%%commented_by_linked%%[[/span]] / At: [[span class="lp_commented_at"]]%%commented_at%%[[/span]] / Total Comments: [[span class="lp_comments"]]%%comments%%[[/span]]
> Rating: [[span class="lp_rating"]]%%rating%%[[/span]] / Total Votes: [[span class="lp_totalvotes"]]%%rating_votes%%[[/span]] / UV: [[span class="lp_uv"]][[#expr %%rating_votes%%-((%%rating_votes%%-%%rating%%)/2)]][[/span]] / DV: [[span class="lp_dv"]][[#expr (%%rating_votes%%-%%rating%%)/2]][[/span]]
> Tags: [[span class="lp_tags"]]%%tags_linked%%[[/span]] / [[span class="lp_hiddentags"]]%%_tags_linked%%[[/span]]
> Parent Pages: [[span class="lp_parent"]]%%parent_title_linked%%[[/span]] ( [[span class="lp_parentdir"]]/%%parent_fullname%%[[/span]] ) / Children Pages: [[span class="lp_children"]]%%children%%[[/span]]
> Size: [[span class="lp_size"]]%%size%%[[/span]]
[[/module]]
```

この場合はコンテストタグつき、批評待ち状態用

dataフォルダにconfig.iniとgoogleAPIのjsonを配置します。googleAPIのjson名google_spread_sheet_handlerの該当部分を書き換えます。  
config.iniには

``` json
[DEFAULT]
name = listpage_watcher
avatar_url = https://raw.githubusercontent.com/being24/wikdot-watcher/master/data/logo.png
WEBHOOK_URL = "your webhook url here"
spreadsheet_key = "your spread sheet key here"
```

上記コードを貼ったページを用意します。

``` json
    "ルーキーコンテスト": {
        "root_url": "http://scp-jp.wikidot.com/author:ukwhatn",
        "lp_tags": [
            "ルーキーコンテスト"
        ],
        "lp_limit": [
            999999
        ]
    }
```

上記のようにwatchlist.jsonを改変します。複数も可能です。  
config.iniに設定したスプレッドシートに情報が書き込まれ、指定のwebhookに投稿します。必要なければ送信部分をコメントアウトしてください。