import json
import os

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

extension_icon = 'images/icon.png'
data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "emoticons.json")


class GitmojiExtension(Extension):

    def __init__(self):
        super(GitmojiExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.emoticons = []

        # Load emoticons from JSON
        with open(data_path) as f:
            data = json.load(f)

        for emoticon in data["emoticons"]:
            # Prepare tokens used for search.
            emoticon["tokens"] = [emoticon["name"].lower()]
            self.emoticons.append(emoticon)


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        searchArg = event.get_argument()
        if searchArg is None or searchArg == "" or searchArg == "*":
            matches = []
        else:
            matches = []
            needles = searchArg.lower().split()

            for emoticon in extension.emoticons:
                matchCount = self.count_matches(emoticon["tokens"], needles)
                if matchCount > 0:
                    result = dict()
                    result.update(emoticon)
                    result["matchCount"] = matchCount
                    matches.append(result)

            matches = sorted(matches[:10], key=lambda data: data["matchCount"], reverse=True)

        return RenderResultListAction([
            self.build_result_item(match, extension) for match in matches
        ])

    def build_result_item(self, match, extension):
        main_action = CopyToClipboardAction(match['code'])
        alt_action = CopyToClipboardAction(match['code'])

        return ExtensionResultItem(
            icon='images/sub-icon.png',
            name=match['code'],
#            description=match['description'],
            on_enter=main_action,
            on_alt_enter=alt_action
        )

    def count_matches(self, tokens, needles):
        count = 0
        for token in tokens:
            for needle in needles:
                if needle in token:
                    count += 1
        return count


if __name__ == '__main__':
    GitmojiExtension().run()
