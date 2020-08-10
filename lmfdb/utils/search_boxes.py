from .utilities import display_knowl, get_css_grid_classes, px_to_em
from sage.structure.unique_representation import UniqueRepresentation

'''
Update: 
  - td -> div
  - colspan and rowspan should be replaced in the future
  - instead use css_classes as the parameter css_grid.
'''

class DivElt(object):
    #_wrap_type = 'td'
    _wrap_type = 'div'
    _closing_tag = '</%s>' % _wrap_type
    def _add_class(self, D, clsname):
        if 'class' in D:
            D['class'] = D['class'] + ' ' + clsname
        else:
            D['class'] = clsname

    def _wrap(self, typ, **kwds):
        keys = []
        kwds = dict(kwds)
        if hasattr(self, "wrap_mixins"):
            kwds.update(self.wrap_mixins)
        if self.advanced:
            self._add_class(kwds, 'advanced')
        for key, val in kwds.items():
            keys.append(' %s="%s"' % (key, val))
        return "<%s%s>" % (typ, "".join(keys))

    def wrap(self, colspan=None, classes=[], inner_html="", **kwds):
        classes.append(self.__class__.__name__)
        if colspan is not None:
            kwds['colspan'] = colspan
        if len(classes) != 0:
            kwds['class'] = " ".join(classes)
        if inner_html == None:
            inner_html = ""
        return self._wrap(self._wrap_type, **kwds) + inner_html + self._closing_tag
        
class EmptySpacer(DivElt):
    '''
    We should use this one for empty space in the grid, via css classes.
    '''
    
    def __init__(self, css_grid=None, advanced=False, css_class=None):
        self.css_grid = get_css_grid_classes()["default"] if css_grid is None else css_grid
        self.css_class = "" if css_class is None else css_class
        self.advanced = advanced;
    
    def input_html(self, info=None):
        return ""

    def label_html(self, info=None):
        return ""

    def example_html(self, info=None):
        return ""
        
    def html(self, info=None):
        label = self.label_html(info)
        input_ = self.input_html(info)
        example = self.example_html(info)
        inner_html = ""
        if label != None:
            inner_html += label
        if input_ != None:
            inner_html += input_
        if example != None:
            inner_html += example
            
        result = self.wrap(classes=[self.css_class,self.css_grid],
                           inner_html=inner_html)
        return result
        
#we keep this for legacy, colspan is not used anymore
class Spacer(EmptySpacer):
    def __init__(self, colspan=None, advanced=False, css_grid=None):
        self.colspan = colspan
        super().__init__(css_grid=css_grid, advanced=advanced)

    def has_label(self, info=None):
        return False

#legacy:
class RowSpacer(Spacer):
    def __init__(self, rowheight, advanced=False):
        self.rowheight = rowheight
        self.advanced = advanced

    def html(self, info=None):
        return self.wrap(classes=["form-rowspacer","col-all"],
                         style = "height:%sem" % px_to_em(self.rowheight))

#legacy:
class BasicSpacer(Spacer):
    def __init__(self, msg, colspan=1, advanced=False):
        Spacer.__init__(self, colspan=colspan, advanced=advanced)
        self.msg = msg

    def input_html(self, info=None):
        return self.msg 
        #return self.wrap(self.colspan,inner_html=self.msg,classes=["spacer-msg"])

#legacy:
class CheckboxSpacer(Spacer):
    def __init__(self, checkbox, colspan=1, advanced=False):
        Spacer.__init__(self, colspan=colspan, advanced=advanced)
        self.checkbox = checkbox

    def html(self, info=None):
        inner_html = self.checkbox._label(info) + " " + self.checkbox._input(info)
        return self.wrap(self.colspan, classes=["form-checkbox","col-all"], inner_html=inner_html)

class SearchBox(EmptySpacer):
    """
    Class abstracting the input boxes used for LMFDB searches.
    """
    _default_width = 160

    def __init__(
        self,
        name=None,
        label=None,
        knowl=None,
        example=None,
        example_span=None,
        example_span_colspan=1,
        colspan=(1, 1, 1), #outdated, use css_grid instead
        rowspan=(1, 1), #outdated
        width=None,
        short_width=None,
        short_label=None,
        advanced=False,
        example_col=False,
        id=None,
        qfield=None,
        css_class=None,
        css_grid=None
    ):
        self.name = name
        self.id = id
        self.label = label
        self.knowl = knowl
        self.example = example
        self.example_span = example if example_span is None else example_span
        self.example_span_colspan = example_span_colspan
        if example_col is None:
            example_col = bool(self.example_span)
        self.example_col = example_col
        self.label_colspan, self.input_colspan, self.short_colspan = colspan
        self.label_rowspan, self.input_rowspan = rowspan
        if short_label is None:
            short_label = label
        self.short_label = short_label
        self.qfield = name if qfield is None else qfield
        if width is None:
            width = self._default_width
        self.width = width
        self.short_width = self.width if short_width is None else short_width
        self.css_class = "search-box" if css_class is None else css_class
        super().__init__(css_grid=css_grid,advanced=advanced,css_class=self.css_class)

    def _label(self, info):
        label = self.label if info is None else self.short_label
        if self.knowl is not None:
            label = display_knowl(self.knowl, label)
        return label

    def has_label(self, info):
        label = self.label if info is None else self.short_label
        return bool(label)

    def label_html(self, info=None):
        colspan = self.label_colspan if info is None else self.short_colspan
        return self.wrap(colspan, rowspan=self.label_rowspan, classes=["form-label"],
                         inner_html=self._label(info))

    def input_html(self, info=None):
        colspan = self.input_colspan if info is None else self.short_colspan
        return self.wrap(colspan, rowspan=self.input_rowspan, classes=['form-inputs'],
                         inner_html=self._input(info))

    def example_html(self, info=None):
        #TODO: check:
        if self.example_span:
            return '<div class="formexample">e.g. %s</div>' % self.example_span
        elif self.example_col:
            return '<div class="formexample"></div>'

    def html(self, info=None):
        label = self.label_html(info)
        input_ = self.input_html(info)
        example = self.example_html(info)
        inner_html = ""
        if label != None:
            inner_html += label
        if input_ != None:
            inner_html += input_
        if example != None:
            inner_html += example
            
        result = self.wrap(classes=[self.css_class,self.css_grid],
                           inner_html=inner_html)
        return result

class TextBox(SearchBox):
    """
    A text box for user input.

    INPUT:

    - ``name`` -- the name of the input (will show up in URL)
    - ``label`` -- the label for the input, shown on browse page
    - ``knowl`` -- a knowl id to apply to the label (you can set as None include a display_knowl directly in the label/short_label if the whole text shouldn't be a knowl link)
    - ``example`` -- the example in the input box
    - ``example_span`` -- the formexample span (defaults to example)
    - ``width`` -- the width of the input element on the browse page
    - ``short_width`` -- the width of the input element on the refine-search page (defaults to width)
    - ``short_label`` -- the label on the refine-search page, if different
    - ``qfield`` -- the corresponding database column (defaults to name).  Not currently used.
    """

    def __init__(
        self,
        name=None,
        label=None,
        knowl=None,
        example=None,
        example_span=None,
        example_span_colspan=1,
        example_value=False,
        colspan=(1, 1, 1),
        rowspan=(1, 1),
        width=160,
        short_width=None,
        short_label=None,
        advanced=False,
        example_col=None,
        id=None,
        qfield=None,
        extra=[],
        css_class=None,
        css_grid=None
    ):
        SearchBox.__init__(
            self,
            name,
            label,
            knowl=knowl,
            example=example,
            example_span=example_span,
            example_span_colspan=example_span_colspan,
            colspan=colspan,
            rowspan=rowspan,
            width=width,
            short_width=short_width,
            short_label=short_label,
            advanced=advanced,
            example_col=example_col,
            id=id,
            qfield=qfield,
            css_class=css_class,
            css_grid=css_grid
        )
        self.extra = extra
        self.example_value = example_value

    def _input(self, info):
        keys = self.extra + ['type="text"', 'name="%s"' % self.name]
        if self.id is not None:
            keys.append('id="%s"' % self.id)
        if self.advanced:
            keys.append('class="advanced"')
        if self.example is not None:
            if self.example_value and info is None:
                keys.append('value="%s"' % self.example)
            else:
                keys.append('placeholder="%s"' % self.example)
        #if info is None:
        #    if self.width is not None:
        #        keys.append('style="width: %sem"' % px_to_em(self.width))
        if info is not None:
            #if self.short_width is not None:
            #    keys.append('style="width: %sem"' % px_to_em(self.short_width))
            if self.name in info:
                keys.append('value="%s"' % info[self.name])
        return '<input type="text" ' + " ".join(keys) + "/>"

class SelectBox(SearchBox):
    """
    A select box for user input.

    INPUT:

    - ``name`` -- the name of the input (will show up in URL)
    - ``label`` -- the label for the input, shown on browse page
    - ``options`` -- list of tuples (value, option) for the select options
    - ``knowl`` -- a knowl id to apply to the label (you can set as None include a display_knowl directly in the label/short_label if the whole text shouldn't be a knowl link)
    - ``width`` -- the width of the input element on the browse page
    - ``short_width`` -- the width of the input element on the refine-search page (defaults to width)
    - ``short_label`` -- the label on the refine-search page, if different
    - ``qfield`` -- the corresponding database column (defaults to name).  Not currently used.
    """
    _options = []
    _default_width = 170

    def __init__(
        self,
        name=None,
        label=None,
        options=None,
        knowl=None,
        example=None,
        example_span=None,
        example_span_colspan=1,
        colspan=(1, 1, 1),
        rowspan=(1, 1),
        width=None,
        short_width=None,
        short_label=None,
        advanced=False,
        example_col=False,
        id=None,
        qfield=None,
        extra=[],
        css_class=None,
        css_grid=None
    ):
        SearchBox.__init__(
            self,
            name,
            label,
            knowl=knowl,
            example=example,
            example_span=example_span,
            example_span_colspan=example_span_colspan,
            colspan=colspan,
            rowspan=rowspan,
            width=width,
            short_width=short_width,
            short_label=short_label,
            advanced=advanced,
            example_col=example_col,
            id=id,
            qfield=qfield,
            css_class=css_class,
            css_grid=css_grid
        )
        if options is None:
            options = self._options
        self.options = options
        self.extra = extra

    def _input(self, info):
        keys = self.extra + ['name="%s"' % self.name]
        if self.id is not None:
            keys.append('id="%s"' % self.id)
        if self.advanced:
            keys.append('class="advanced"')
        #if info is None:
        #    if self.width is not None:
        #        keys.append('style="width: %sem"' % px_to_em(self.width))
        #else:
        #    if self.short_width is not None:
        #        keys.append('style="width: %sem"' % px_to_em(self.short_width))
        opts = []
        for value, display in self.options:
            if (
                info is None
                and value == ""
                or info is not None
                and info.get(self.name, "") == value
            ):
                selected = " selected"
            else:
                selected = ""
            if value is None:
                value = ""
            else:
                value = 'value="%s"' % value
            opts.append("<option %s%s>%s</option>" % (value, selected, display))
        return "        <select %s>\n%s\n        </select>" % (
            " ".join(keys),
            "".join("\n" + " " * 10 + opt for opt in opts),
        )

class NoEg(SearchBox):
    def example_html(self, info=None):
        return self.wrap(self.example_span_colspan, classes=["formexample"],
                         inner_html=self.example_span)

class TextBoxNoEg(NoEg, TextBox):
    pass

class SelectBoxNoEg(NoEg, SelectBox):
    pass

class HiddenBox(SearchBox):
    def _input(self, info=None):
        keys = ['name="%s"' % self.name]
        if self.advanced:
            keys.append('class="advanced"')
        if info is not None and info.get(self.name):
            keys.append('value="%s"' % info.get(self.name))
        return '<input type="hidden" %s>' % (" ".join(keys),)

class CheckBox(SearchBox):
    def _input(self, info=None):
        keys = ['name="%s"' % self.name, 'value="yes"']
        if self.advanced:
            keys.append('class="advanced"')
        if info is not None and info.get(self.name, False):
            keys.append("checked")
        return '<input type="checkbox" %s>' % (" ".join(keys),)


class SkipBox(TextBox):
    def _input(self, info=None):
        return ""

    def _label(self, info=None):
        return ""


class TextBoxWithSelect(TextBox):
    def __init__(self, name, label, select_box, **kwds):
        self.select_box = select_box
        TextBox.__init__(self, name, label, **kwds)

    '''
    def label_html(self, info=None):
        colspan = self.label_colspan if info is None else self.short_colspan
        return (
            self.div(colspan)
            + '<div style="display: flex; justify-content: space-between;">'
            + self._label(info)
            + '<span style="margin-left: 0.3em;"></span>'
            + self.select_box._input(info)
            + "</div>"
            + "</div>"
        )
    '''
    
    def _input(self, info=None):
        #print("super:",super,type(super))
        inner_html = '<table><tr><td>'+self.select_box._input(info)+'</td>'
        inner_html += '<td width="100%">'+super()._input(info)+'</td></tr></table>'
        return inner_html;
        #return self.select_box._input(info) + super()._input(info)

class DoubleSelectBox(SearchBox):
    def __init__(self, label, select_box1, select_box2, **kwds):
        self.select_box1 = select_box1
        self.select_box2 = select_box2
        SearchBox.__init__(self, label, **kwds)
        #TODO: add css class for this particular input type

    def _input(self, info):
        inner_html = '<table width="100%"><tr><td width="50%">' + self.select_box1._input(info) + '</td>'
        inner_html += '<td width="50%">' + self.select_box2._input(info) + '</td></tr></table>'
        return inner_html
        #return self.select_box1._input(info) + self.select_box2._input(info);
 
class ExcludeOnlyBox(SelectBox):
    _options = [("", ""),
                ("exclude", "exclude"),
                ("only", "only")]

class YesNoBox(SelectBox):
    _options = [("", ""),
                ("yes", "yes"),
                ("no", "no")]

class YesNoMaybeBox(SelectBox):
    _options = [("", ""),
                ("yes", "yes"),
                ("not_no", "yes or unknown"),
                ("not_yes", "no or unknown"),
                ("no", "no"),
                ("unknown", "unknown")]

class ParityBox(SelectBox):
    _options = [('', ''),
                ('even', 'even'),
                ('odd', 'odd')]

class ParityMod(SelectBox):
    _default_width = 85
    # For modifying a text box
    _options = [('', 'any parity'),
                ('even', 'even only'),
                ('odd', 'odd only')]


class SubsetBox(SelectBox):
    _default_width = 60
    _options = [('', 'include'),
                ('exclude', 'exclude'),
                ('exactly', 'exactly'),
                ('subset', 'subset')]

class SubsetNoExcludeBox(SelectBox):
    _default_width = 60
    _options = [('', 'include'),
                ('exactly', 'exactly'),
                ('subset', 'subset')]

class CountBox(TextBox):
    def __init__(self,css_grid=None):
        TextBox.__init__(
            self,
            name="count",
            label="Results to display",
            example=50,
            example_col=True,
            example_value=True,
            example_span="",
            css_grid=css_grid)

class SearchButton(SearchBox):
    _default_width = 170
    def __init__(self, value, description, **kwds):
        kwds['label'] = kwds.get('label', '')
        SearchBox.__init__(self, **kwds)
        self.value = value
        self.description = description

    def wrap(self, colspan=None, classes=[], inner_html="", **kwds):
        kwds = dict(kwds)
        self._add_class(kwds, 'button')
        return SearchBox.wrap(self, colspan, classes, inner_html, **kwds)

    def _input(self, info):
        if info is None:
            onclick = ""
        else:
            onclick = " onclick='resetStart()'"
        btext = "<button type='submit' name='search_type' value='{val}' style='width: {width}em;'{onclick}>{desc}</button>"
        return btext.format(
            width = px_to_em(self.width),
            val = self.value,
            desc = self.description,
            onclick = onclick,
        )

class SearchButtonWithSelect(SearchButton):
    def __init__(self, value, description, select_box, **kwds):
        self.select_box = select_box
        SearchButton.__init__(self, value, description, **kwds)

    def label_html(self, info=None):
        colspan = self.label_colspan if info is None else self.short_colspan
        inner_html = self._label(info) + self.select_box._input(info)
        return self.wrap(colspan,classes=["button-with-select"],
                         inner_html=inner_html)

class SearchArray(UniqueRepresentation):
    """
    This class is used to represent the grid of inputs in a browse or search array.
    The goal is to be able to use create one object for each input which can then
    be reused in multiple locations.

    You should set the following attributes/functions to make this work.

    - ``browse_array`` and ``refine_array`` -- each a list of lists of ``SearchBox`` objects.
        You can also override ``main_array()`` for more flexibility.
        Will be passed ``info=None`` for the browse page, or the info dictionary for refining search
    - ``sort_order`` -- a function of ``info`` returning a list of pairs, the url value
        and display value for the sort options.  You may also want to set the ``sort_knowl`` attribute
    - ``search_types`` -- returns a list of pairs giving the url value and display value
        for the search buttons
    - ``hidden`` -- returns a list of pairs giving the name and info key for the hidden inputs
    """
    _ex_col_width = 170 # only used for box layout
    sort_knowl = None
    noun = "result"
    plural_noun = "results"
    def sort_order(self, info):
        # Override this method to add a dropdown for sort order
        return None

    def _search_again(self, info, search_types):
        if info is None:
            return search_types
        st = self._st(info)
        return [(st, "Search again")] + [(v, d) for v, d in search_types if v != st]

    def search_types(self, info):
        # Override this method to change the displayed search buttons
        if info is None:
            return [("List", "List of %s" % self.plural_noun), ("Random", "Random %s" % self.noun)]
        else:
            return [("List", "Search again"), ("Random", "Random %s" % self.noun)]

    def hidden(self, info):
        # Override this method to change the hidden inputs
        return [("start", "start"), ("count", "count"), ("hst", "search_type")]

    def main_array(self, info):
        if info is None:
            return self.browse_array
        else:
            return self.refine_array

    def _print_grid(self, grid, info, layout_type):
        if not grid:
            return ""
            
        #print("grid:",grid)
        print("--- info:",info)
        
        #In the new grid layout, we basically flatten the list of lists grid:
        inner_html = ""
        for row in grid:
            print("row:",row)
            if isinstance(row, Spacer):
                inner_html += row.html(info)
                continue
            for element in row:
                print("element:",element)
                inner_html += element.html(info)
        result = '<div class="grid12">' + inner_html + "</div>"
        return result
        
    def _st(self, info):
        if info is not None:
            return info.get("search_type", info.get("hst", "List"))

    def dynstats_array(self, info):
        if self._st(info) == "DynStats":
            array = [RowSpacer(30)]
            vheader = BasicSpacer("Variables")
            vheader.wrap_mixins = {"class": "table_h2"}
            array.append([vheader])
            for i in [1,2]:
                cols = SelectBox(
                    name="col%s" % i,
                    id="col%s_select" % i,
                    label="",
                    width=150,
                    options=info["stats"]._dynamic_cols,
                    extra=['onchange="set_buckets(this, \'buckets%s\')"'%i])
                buckets = TextBox(
                    name="buckets%s" % i,
                    id="buckets%s" % i,
                    label="Buckets" if i == 1 else "",
                    knowl="stats.buckets" if i == 1 else None,
                    width=310)
                totals = CheckBox(
                    name="totals%s" % i,
                    label="Totals" if i == 1 else "",
                    knowl="stats.totals" if i == 1 else None)
                proportions = SelectBox(
                    name="proportions",
                    width=150,
                    options=[("recurse", "Vs unconstrained"),
                             ("rows", "By rows"),
                             ("cols", "By columns"),
                             ("none", "None")],
                    label="Proportions" if i == 1 else "",
                    rowspan=(1, 2),
                    knowl="stats.proportions" if i == 1 else None)
                if i == 1:
                    array.append([cols, buckets, totals, proportions])
                else:
                    array.append([cols, buckets, totals])
            return array
        else:
            return []

    def hidden_inputs(self, info=None):
        if info is None:
            return ""
        else:
            return "\n".join('<input type="hidden" name="%s" value="%s"/>' % (name, info.get(val)) for (name, val) in self.hidden(info))

    def main_table(self, info=None):
        layout_type = "horizontal" if info is None else "vertical"
        s = self._print_grid(self.main_array(info), info, layout_type=layout_type)
        dstats = self.dynstats_array(info)
        if dstats:
            s += "\n" + self._print_grid(dstats, info, layout_type=layout_type)
        return s

    def has_advanced_inputs(self, info=None):
        for row in self.main_array(info):
            if isinstance(row, DivElt) and row.advanced:
                return True
            for col in row:
                if col.advanced:
                    return True
        return False

    def buttons(self, info=None):
        caption = None
        st = self._st(info)
        buttons = []
        if st == "DynStats":
            buttons.append(SearchButton("DynStats", "Generate statistics"))
        else:
            if st is None:
                caption = "Display:"
            for but in self.search_types(info):
                if isinstance(but, DivElt):
                    buttons.append(but)
                else:
                    buttons.append(SearchButton(*but))
            if st is not None:
                sort = self.sort_order(info)
                if sort:
                    sort_box = SelectBox(
                        name='sort_order',
                        label='Sort order',
                        knowl=self.sort_knowl,
                        options=sort,
                        width=170)
                    buttons.append(sort_box)
        #OLD:
        #return self._print_grid([RowSpacer(22), buttons], info, layout_type="vertical")

        button_container = '<div class="button-container">' + \
                           " ".join(but.html() for but in buttons) + \
                           '</div>'          
        if caption is None:
            result = button_container
        else:
            result = '<table width="100%"><tr><td width="10%">' + caption + '</td>' + \
                    '<td>' + button_container + '</td></tr></table>'
        return '<p>' + result + '</p>'

    def html(self, info=None):
        return "\n".join([self.hidden_inputs(info), self.main_table(info), self.buttons(info)])

    def jump_box(self, info):
        jump_example = info.get("jump_example", getattr(self, "jump_example", ""))
        jump_width = info.get("jump_width", getattr(self, "jump_width", 320))
        jump_egspan = info.get("jump_egspan", getattr(self, "jump_egspan", ""))
        # We don't use SearchBoxes since we want the example to be below, and the button directly to the right of the input (regardless of how big the example is)
        return """<p><input type='text' name='jump' placeholder='%s' style='width:%sem;' value='%s'>
<button type='submit'>Find</button>
<br><span class='formexample'>%s</span></p>""" % (jump_example, px_to_em(jump_width), info.get("jump", ""), jump_egspan)
