# Axiris integrations

Your app can add its own results to the **Axiris search**: photos from a gallery, tracks from a
player, tasks from a to-do app, people from a birthday app, anything that has a name. There is no
library to add and no permission to request: you write one `ContentProvider`, declare it in your
manifest, and the user switches your app on in **Axiris > Settings > Search**.

Axiris never reads anything from an app the user has not switched on.

## 1. Declare the provider

```xml
<provider
    android:name=".AxirisSearch"
    android:authorities="${applicationId}.axiris"
    android:exported="true">
    <intent-filter>
        <action android:name="com.minar.axiris.action.INTEGRATION" />
        <category android:name="android.intent.category.DEFAULT" />
    </intent-filter>
</provider>
```

- `android:authorities` must be unique on the device. Suffixing your application id is the easy way.
  **Do not change it later**: it is how Axiris remembers that the user switched your app on.
- `exported="true"` is required, because Axiris is another app. Section 4 shows how to answer only
  Axiris.

## 2. Answer one query

While the user types, Axiris calls `query()` on:

```
content://<authority>/search?q=<what the user typed>&limit=<how many rows>
```

Return the rows that match, best first, at most `limit` of them.

## 3. The columns

Only `title` is required. Unknown columns are ignored, and missing ones fall back as described.

| Column | Type | What it is | If missing |
| --- | --- | --- | --- |
| `title` | TEXT | The main line: a name, a song, a task. | The row is skipped. |
| `id` | TEXT | A stable id for the row. | The title is used. |
| `subtitle` | TEXT | The second line: an artist, a date, a folder. | One line only. |
| `extra` | TEXT | A short value at the end of the row: `3:45`, `in 12 days`, `12 photos`. Up to 24 characters. | Nothing at the end. |
| `image` | BLOB | A PNG or JPEG, at most 256 KB. Keep it small: it is shown at about 40 dp. | Your app's icon. |
| `image_shape` | TEXT | `square` for covers, photos and thumbnails, `round` for people and icons. | `round`. |
| `intent` | TEXT | What opens on tap, as `Intent.toUri(Intent.URI_INTENT_SCHEME)`. | Your app opens. |

Text is cut at 200 characters.

### What happens to your intent

For safety, Axiris always opens your intent **inside your own app**: it sets the package to yours,
drops any selector and any URI permission flag, and falls back to launching your app when the intent
does not resolve. Point it at an exported activity of yours.

## 4. Answer only Axiris

Your provider is exported, so check who is asking and return `null` to anybody else:

```kotlin
private val AXIRIS = setOf("com.minar.axiris", "com.minar.axiris.dev")

private fun allowed() = callingPackage in AXIRIS
```

`ContentProvider.getCallingPackage()` is filled in by the system and cannot be faked by the caller.

## 5. A complete example

```kotlin
class AxirisSearch : ContentProvider() {

    override fun onCreate() = true

    override fun query(
        uri: Uri, projection: Array<out String>?, selection: String?,
        selectionArgs: Array<out String>?, sortOrder: String?
    ): Cursor? {
        if (callingPackage !in setOf("com.minar.axiris", "com.minar.axiris.dev")) return null
        if (uri.lastPathSegment != "search") return null
        val query = uri.getQueryParameter("q").orEmpty()
        val limit = uri.getQueryParameter("limit")?.toIntOrNull() ?: 5

        val cursor = MatrixCursor(arrayOf("id", "title", "subtitle", "extra", "image", "image_shape", "intent"))
        repository.find(query).take(limit).forEach { item ->
            cursor.addRow(
                arrayOf(
                    item.id,
                    item.title,
                    item.subtitle,
                    item.extra,
                    item.thumbnailPng,          // ByteArray, or null
                    "square",
                    Intent(context, DetailsActivity::class.java)
                        .putExtra("id", item.id)
                        .toUri(Intent.URI_INTENT_SCHEME)
                )
            )
        }
        return cursor
    }

    // Read only: Axiris never writes
    override fun getType(uri: Uri): String? = null
    override fun insert(uri: Uri, values: ContentValues?): Uri? = null
    override fun delete(uri: Uri, selection: String?, selectionArgs: Array<out String>?) = 0
    override fun update(uri: Uri, values: ContentValues?, selection: String?, selectionArgs: Array<out String>?) = 0
}
```

`query()` runs on a binder thread, so a database read is fine. Axiris asks while the user types and
shows the answers as they arrive: be quick, and cache anything slow.

## 6. Try it

1. Install your app and Axiris.
2. Open **Axiris > Settings > Search** and scroll to the end: your app is listed.
3. Switch it on, then search for something your app knows about.

If your app is not listed, check that the provider is exported and that the action is spelled
exactly as above.

## Who uses it
[Birday](https://github.com/m-i-n-a-r/birday), my app for birthdays and anniversaries, was the first: search a
name in Axiris and you get the event, with how many days are left and the picture of the person. Its provider
is a good real world example to start from.

Built an integration? Tell me in an [issue](https://github.com/m-i-n-a-r/axiris/issues) or on
[r/axirislauncher](https://www.reddit.com/r/axirislauncher/): I'll gladly list your app here.

## Questions
Something unclear, or a column you'd need? Open an [issue](https://github.com/m-i-n-a-r/axiris/issues).

## Versioning

This is version 1 of the contract. New columns may be added in future versions and will always be
optional: an app written against version 1 keeps working.
