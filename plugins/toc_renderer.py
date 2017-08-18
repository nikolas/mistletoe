"""
Table of contents support for mistletoe.

See `if __name__ == '__main__'` section for sample usage.
"""

import re
from mistletoe.html_renderer import HTMLRenderer


class TOCRenderer(HTMLRenderer):
    """
    Extends HTMLRenderer class for table of contents support.

    Args:
        depth (int): the maximum level of heading to be included in TOC;
        omit_title (bool): whether to ignore tokens where token.level == 1;
        filter_conds (list): when any of these functions evaluate to true,
                             current heading will not be included;
        extras (list): allows subclasses to add even more custom tokens.
    """
    def __init__(self, depth=5, omit_title=True, filter_conds=[], *extras):
        super().__init__(*extras)
        self._headings = []
        self.depth = depth
        self.omit_title = omit_title
        self.filter_conds = filter_conds

    @property
    def toc(self):
        """
        Returns table of contents as a block_token.List instance.
        """
        from mistletoe.block_token import List
        def get_indent(level):
            if self.omit_title:
                level -= 1
            return ' ' * 4 * (level - 1)

        def build_list_item(heading):
            level, content = heading
            template = '{indent}- {content}\n'
            return template.format(indent=get_indent(level), content=content)

        return List([build_list_item(heading) for heading in self._headings])

    def render_heading(self, token, footnotes):
        """
        Overrides super().render_heading; stores rendered heading first,
        then returns it.
        """
        rendered = super().render_heading(token, footnotes)
        content = self.parse_rendered_heading(rendered)
        if not (self.omit_title and token.level == 1
                or token.level > self.depth
                or any(cond(content) for cond in self.filter_conds)):
            self._headings.append((token.level, content))
        return rendered

    @staticmethod
    def parse_rendered_heading(rendered):
        """
        Helper method; converts rendered heading to plain text.
        """
        return re.sub(r'<.+?>', '', rendered[4:-6])
