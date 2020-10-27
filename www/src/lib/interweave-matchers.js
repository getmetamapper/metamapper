import React from "react"
import { Matcher } from "interweave"

export class MarkdownUrlMatcher extends Matcher<CustomProps> {
  match(string: string): MatchResponse<{ extraProp: string }> | null {
    const result = string.match(/\[(.*?)\]\((.*?)\)/);

    if (!result) {
      return null;
    }

    return {
      index: result.index,
      length: result[0].length,
      match: result[1],
      href: result[2],
      valid: true,
    };
  }

  replaceWith(children: ChildrenNode, props: CustomProps): Node {
    return <a {...props} target="_blank">{children}</a>;
  }

  asTag(): string {
    return 'a';
  }
}
