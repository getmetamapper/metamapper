import React from "react"
import { Tag } from "antd"

const MultiSelectDisplay = ({ value }) => <span>{value.map(v => <Tag color="volcano">{v}</Tag>)}</span>

export default MultiSelectDisplay
