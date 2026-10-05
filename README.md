# todo-age

`TODO` はいつ書かれた? 誰が書いた? — リポジトリ内の TODO / FIXME / HACK / XXX を `git blame` で調べ、**古い順**に一覧表示する依存ゼロの CLI (Python 3, 単一ファイル)。

```
$ python todo_age.py --min-days 180
  912d  TODO  src/db.py:88  (alice)  remove this workaround
  400d  FIXME api/auth.py:21  (bob)  handle token expiry
```

## 使い方
```
python todo_age.py [--min-days N] [--json] [--fail-over DAYS]
```
- `--min-days N` N日以上前のものだけ表示
- `--json` JSON 出力
- `--fail-over DAYS` DAYS より古い TODO があれば終了コード 1 (CI で「放置TODO」を防ぐ)

### GitHub Actions 例
```yaml
- uses: actions/checkout@v4
  with: { fetch-depth: 0 }
- run: python todo_age.py --fail-over 365
```

## テスト
`python -m unittest discover tests`

## License
MIT
