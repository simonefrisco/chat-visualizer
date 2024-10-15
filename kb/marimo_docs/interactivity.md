Interactivity
One of marimo’s most powerful features is its first-class support for interactive, stateful user interface (UI) elements, or “widgets”: create them using marimo.ui. Interacting with a UI element bound to a global variable automatically runs all cells that reference it.


How interactions run cells
Every UI element you make using marimo.ui has a value, accessible via its value attribute. When you interact with a UI element bound to a global variable, its value is sent back to Python. A single rule determines what happens next:

Interaction rule

When a UI element assigned to a global variable is interacted with, marimo automatically runs all cells that reference the variable (but don’t define it).

In the clip at the top of this page, interacting with the slider in the second cell re-runs the third cell (which outputs markdown) because it references the slider variable x. It doesn’t re-run the second cell, because that cell defines x.

For interactions on a UI element to have any effect, the element must be assigned to a global variable.

Displaying UI elements
Display UI elements in the output area above a cell by including them in the last expression, just like any other object. You can also embed elements in markdown using Python f-strings, like so:

slider = mo.ui.slider(1, 10)
mo.md(f"Choose a value: {slider})")
Composite elements
Composite elements are advanced elements let you build UI elements out of other UI elements. The following composite elements are available:

mo.ui.array

mo.ui.dictionary

mo.ui.batch

mo.ui.form

Arrays and dictionaries. Use mo.ui.array and mo.ui.dictionary to logically group together related elements. These elements are especially useful when a set of UI elements is only known at runtime (so you can’t assign each to a global variable individually, but can assign them to an array or dictionary).

You can access the elements contained in an array or dictionary using Pythonic syntax, and embed these elements in other outputs. See their docstrings for code examples.

Batch and form. Use these powerful elements to group together multiple UI elements into a single element with custom formatting, and gate the sending of an element’s value on form submission.


Use a form to gate value updates on submission

Use an array to group together elements or create a collection of elements that is determined at runtime
Building custom UI elements using our plugin API
You can build your own reactive and interactive UI elements using anywidget! See our docs on building custom UI elements to learn more.