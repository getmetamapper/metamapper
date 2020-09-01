import React from "react"
import { map } from "lodash"
import withGetObjectComments from "graphql/withGetObjectComments"
import Comment from "./Comment"

const CommentThread = ({ comments, contentObject, onCreate, onDelete }) => (
  <div className="comment-thread">
    {map(comments, ({ childComments, ...comment }) => (
      <Comment
        key={comment.id}
        isParent
        childCount={childComments.length}
        contentObject={contentObject}
        onCreate={onCreate}
        onDelete={onDelete}
        {...comment}
      >
        {map(childComments, (child) => (
          <Comment
            key={child.id}
            isParent={false}
            childCount={0}
            contentObject={contentObject}
            onCreate={onCreate}
            onDelete={onDelete}
            {...child}
          />
        ))}
      </Comment>
    ))}
  </div>
)

export default withGetObjectComments(CommentThread)
