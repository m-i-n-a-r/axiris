# Translate Axiris

First of all, thanks! Every language in Axiris could use a native speaker, so even fixing a couple of strings that sound weird is a real help. You'll be credited in the main README and in the Play Store description.

## How it works
- `values/strings.xml` is the English source. Don't edit it: it's copied here from the app at every release, so any change would be overwritten.
- Every other folder is a language, named `values-xx` with the two letter code of the language (only the language, never the region: `values-pt`, not `values-pt-rBR`). Indonesian is the one exception: it's `values-in`, for historical reasons in Android itself.
- [STATUS.md](STATUS.md) shows how many strings each language has, and how many are missing. A missing string simply shows up in English in the app.

## Translating
1. Fork this repository, or just download the file of your language (or `values/strings.xml`, if your language is not there yet).
2. Translate, following the rules below.
3. Open a pull request. If GitHub is not your thing, you can also send me the file by email at minar.tastic@gmail.com.

Every pull request is checked automatically: if something would break the app, the check tells you exactly which line to fix. You can run the same check on your computer with `python translations/check.py`.

## Rules
- **Apostrophes and double quotes need a backslash**: write `\'` and `\"`. Without it, the app doesn't even build.
- **Keep the placeholders**: `%1$s`, `%2$d`, `%d` and so on are replaced by a value when the app runs (a name, a number...). Keep all of them, exactly as they are, and move them where your grammar needs them.
- **No em dashes** (—): Axiris never uses them. Use a comma, or a middle dot (·) in short labels.
- **Plurals**: a `<plurals>` has one form per quantity. Use the quantities your language needs (`one`, `few`, `many`, `other`...), and always include `other`. A plural stays a plural and a string stays a string.
- **Arrays**: a `<string-array>` must keep the same number of items, in the same order.
- **Keep it short**: many strings end up on buttons, chips or next to a switch. If the English is short, there's a reason. The same goes for the tone: Axiris talks in a simple and friendly way, not like a manual.
- **Keep technical words in English** when that's how people say them in your language (widget, launcher, dial...).
- Some names are missing on purpose: they're not meant to be translated, so they don't appear here at all.

## The word clock
The clock can tell the time in words ("twenty past ten"). Since every language counts the time differently, a few entries near the top of the file describe the grammar rather than words:
- `fuzzy_hours` and `fuzzy_phrases`: the hours, and the twelve five-minute phrases (`%1$s` is the hour).
- `fuzzy_next_from`: the first phrase that already names the **next** hour, counting from 0 ("o'clock"). In English that's 7, "twenty-five to", while German already does it at the half hour ("halb eins" is 12:30).
- `fuzzy_cases`, `fuzzy_hours_past` and `fuzzy_hours_to`: only for languages where the hour itself changes form (in Russian, Polish and Turkish, for example). If your language doesn't need them, just leave them out.

Not sure about the word clock? Leave it in English and tell me in the pull request, we'll figure it out together.

## A new language
Your language is not here? Great! Create the `values-xx` folder, copy `values/strings.xml` inside it and start translating: you don't need to finish it in one go, a partial translation is welcome too. I'll take care of adding the new language to the app.
