# rookie-contest-gswatcher

コンテスト用のgsとサイトページの監視スクリプト

googleAPIのjsonは自分でがんばれ

## SB3用のコード

```html
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
