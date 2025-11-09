// ExamKit Typst Theme
// Typography and styling configuration

// Color scheme
#let primary-color = rgb("#2563eb")
#let secondary-color = rgb("#64748b")
#let accent-color = rgb("#f59e0b")
#let background-color = rgb("#ffffff")
#let text-color = rgb("#1e293b")

// Heading styles
#let heading-color = primary-color

// Box styles for callouts
#let note-box(content) = {
  block(
    fill: rgb("#dbeafe"),
    stroke: (left: 3pt + primary-color),
    inset: 10pt,
    radius: 2pt,
    width: 100%,
    [
      *Note:* #content
    ]
  )
}

#let warning-box(content) = {
  block(
    fill: rgb("#fef3c7"),
    stroke: (left: 3pt + accent-color),
    inset: 10pt,
    radius: 2pt,
    width: 100%,
    [
      *⚠️ Warning:* #content
    ]
  )
}

#let example-box(content) = {
  block(
    fill: rgb("#f0fdf4"),
    stroke: (left: 3pt + rgb("#16a34a")),
    inset: 10pt,
    radius: 2pt,
    width: 100%,
    [
      *Example:* #content
    ]
  )
}

#let formula-box(content) = {
  block(
    fill: rgb("#faf5ff"),
    stroke: 1pt + rgb("#a855f7"),
    inset: 10pt,
    radius: 4pt,
    width: 100%,
    align(center)[#content]
  )
}

// Citation style
#let cite-source(source) = {
  text(size: 9pt, fill: secondary-color)[#source]
}

// Theorem-like environments
#let theorem(name, content) = {
  block(
    fill: luma(250),
    stroke: 1pt + luma(200),
    inset: 10pt,
    radius: 2pt,
    width: 100%,
    [
      *#name:* #content
    ]
  )
}
