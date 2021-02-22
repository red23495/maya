var compare_panel = function (id) {
    var panel_div = $(id);
    var close_button = panel_div.find("#compare-close");
    close_button.click(function(e){
        panel_div.hide();
    });
    this.show_compare = function (expected, actual) {
        try{
            expected = to_json(expected);
            actual = to_json(actual);
            panel_div.show();
            diffUsingJS(expected,actual);
        }catch (e) {
            console.log(e);
        }

    }
    // jsview utility
    var diffUsingJS = function (expected, actual) {
        // get the baseText and newText values from the two textboxes, and split them into lines
        var base = difflib.stringAsLines(expected);
        var newtxt = difflib.stringAsLines(actual);
        console.log(base);
        // create a SequenceMatcher instance that diffs the two sets of lines
        var sm = new difflib.SequenceMatcher(base, newtxt);

        // get the opcodes from the SequenceMatcher instance
        // opcodes is a list of 3-tuples describing what changes should be made to the base text
        // in order to yield the new text
        var opcodes = sm.get_opcodes();
        var diffoutputdiv = $("#compare-content");
        diffoutputdiv.html("");
        //while (diffoutputdiv.firstChild) diffoutputdiv.removeChild(diffoutputdiv.firstChild);
        //var contextSize = $("contextSize").value;
        var contextSize = null;
        contextSize = contextSize ? contextSize : null;

        // build the diff view and add it to the current DOM
        diffoutputdiv.append(diffview.buildView({
            baseTextLines: base,
            newTextLines: newtxt,
            opcodes: opcodes,
            // set the display titles for each resource
            baseTextName: "Expected",
            newTextName: "Actual",
            contextSize: contextSize,
            viewType: 0,
        }));

        // scroll down to the diff view window.
        //location = url + "#diff";
    }

    var to_json = function (obj, indent=0) {
        if(typeof obj == "object"){
            if(Array.isArray(obj)){
                return array_to_json(obj,indent);
            }
        }
        var ret = "";
        ret += "{";
        var sorted_keys = Object.keys(obj).sort();
        for(var key in sorted_keys){
            var index = sorted_keys[key];
            var value = obj[index];
            if(typeof value == "undefined") continue;
            ret += "\n";
            for(var i = 0; i < (indent+1)*4; i++) ret += " ";
            ret += '"' + index + '"' + ': ';
            if(typeof value == "object"){
                if(Array.isArray(value)){
                    ret += array_to_json(value, indent+1);
                    ret += ',';
                }
                else{
                    ret += to_json(value,indent+1);
                    ret += ',';
                }
            }
            else{
                ret += JSON.stringify(value)+",";
            }
        }
        ret = ret.slice(0, -1);
        ret += '\n';
        for(var i = 0; i < indent*4; i++) ret += " ";
        ret += "}";
        return ret;
    }

    var array_to_json = function (obj, indent=0) {
        var ret = "";
        ret += "[";
        for(var key in obj){
            var index = key;
            var value = obj[index];
            if(typeof value == "undefined") continue;
            ret += "\n";
            for(var i = 0; i < (indent+1)*4; i++) ret += " ";
            ret += '"' + index + '"' + ': ';
            if(typeof value == "object"){
                if(Array.isArray(value)){
                    ret += array_to_json(value, indent+1);
                    ret += ',';
                }
                else{
                    ret += to_json(value,indent+1);
                    ret += ',';
                }
            }
            else{
                ret += JSON.stringify(value)+",";
            }
        }
        ret = ret.slice(0, -1);
        ret += '\n';
        for(var i = 0; i < indent*4; i++) ret += " ";
        ret += "]";
        return ret;
    }

}
var name_panel = function (id) {
    var panel_div = $(id);
    var close_button = panel_div.find("#name-close");
    var name_button = panel_div.find("button");
    var on_name;
    name_button.click(function (e) {
        if(on_name) on_name(panel_div.find('input').val());
        on_name = null;
        panel_div.hide();
        set_tree_focus();
    });
    close_button.click(function(e){
        panel_div.hide();
        set_tree_focus();
    });
    this.show_name = function (name, button_text , on_name_callback) {
        panel_div.find('input').val(name);
        panel_div.find('button').text(button_text);
        panel_div.show();
        on_name = on_name_callback;
        panel_div.find('input').focus().on("keyup",function (event) {
            if (event.keyCode === 13) {
                name_button.click();
            }
            if (event.keyCode === 27) {
                close_button.click();
            }
        });
    }
    this.show_name = this.show_name.bind(this);
}
var data_panel = function (id) {
    var panel_div = $(id);
    var close_button = panel_div.find("#data-close");
    var heading_div = panel_div.find('#data-heading');
    var code_div = panel_div.find('#data-code');
    close_button.click(function(e){
        panel_div.hide();
    });
    this.show_data = function (heading, data) {
        heading_div.text(heading);
        code_div.text('\n' + JSON.stringify(data, null, 8));
        panel_div.show();
        $(window).on("keyup",function (event) {
            if (event.keyCode === 27) {
                close_button.click();
            }
        })
    }
    this.show_data = this.show_data.bind(this);
}
var expand_container = function(tree_query_string){
    var expanded_keys = [];

    this.storeExpand = function () {
        var tree = $(tree_query_string).fancytree('getTree');
        var nodes = tree.findAll(function (node) {
            return node.isExpanded();
        })
        expanded_keys = nodes.map(function (node) {
            return node.key;
        });
    }
    this.storeExpand = this.storeExpand.bind(this);

    this.swap = function (key1, key2){
        for(var i = 0; i <= expanded_keys.length; i++){
            if(expanded_keys[i] == key1) expanded_keys[i] = key2;
            else if(expanded_keys[i] == key2) expanded_keys[i] = key1;
        }
    }
    this.swap = this.swap.bind(this);

    this.restoreExpand = function () {
        var tree = $(tree_query_string).fancytree('getTree');
        for(var i = 0; i < expanded_keys.length; i++){
            var key = expanded_keys[i];
            tree.getNodeByKey(key).setExpanded(true);
        }
    }
    this.restoreExpand = this.restoreExpand.bind(this);
}
var key_watcher = function (key) {
    var is_key_pressed = false;
    $(window).on("keydown",function (event) {
        if (event.keyCode === key) {
            is_key_pressed = true;
        }
    });
    $(window).on("keyup",function (event) {
        if (event.keyCode === key) {
            is_key_pressed = false;
        }
    });
    this.is_pressed = function () {
        return is_key_pressed;
    };
    this.is_pressed = this.is_pressed.bind(this);
}
var batch_clipboard = function () {
    const MARKED_STYLE = 'in-batch';
    var batch_type = "";
    var batch_list = [];
    var current_filesystem = "";
    var stashed_batch_type = "";
    var stashsed_batch_list = [];
    var stashed_batch_filesystem = "";
    this.is_empty = function () {
        return !batch_type;
    }
    this.is_empty = this.is_empty.bind(this);
    this.toggle_node_in_batch = function (node) {
        var dirtype = node.data.fs_data.type;
        if(this.is_empty()) batch_type = dirtype;
        if(batch_type != dirtype) return;
        switch(dirtype){
            case 'request':
                if(is_valid_filesystem(node)){
                    toggle_request(node);
                }
                break;
            case 'test':
                if(is_valid_filesystem(node)){
                    toggle_tests(node);
                }
                break;
            case 'package':
                if(is_valid_filesystem(node)){
                    toggle_packages(node);
                }
                break;
            case 'filesystem':
                toggle_filesystems(node);
                break;
        }
        if(is_batch_list_empty()){
            this.reset_batch();
        }
    }
    this.toggle_node_in_batch = this.toggle_node_in_batch.bind(this);
    function is_batch_list_empty(){
        return !batch_list.length;
    }
    function toggle_request(node){
        var request_id = node.data.fs_data.req_index;
        if(batch_list.includes(request_id)){
            remove_request(node);
        }else{
            add_request(node);
        }
    }
    function toggle_tests(node) {
        var test_id = node.data.fs_data.test_index;
        if(batch_list.includes(test_id)){
            remove_test(node);
        }else{
            add_test(node);
        }
    }
    function toggle_packages(node) {
        var node_path = node.data.fs_data.path;
        var path_obj = get_path_obj_from_path(node_path);
        var package_name = path_obj.package;
        if(batch_list.includes(package_name)){
            remove_package(node);
        }else{
            add_package(node);
        }
    }
    function toggle_filesystems(node) {
        var node_path = node.data.fs_data.path;
        var path_obj = get_path_obj_from_path(node_path);
        var filesystem_name = path_obj.filesystem;
        if(batch_list.includes(filesystem_name)){
            remove_filesystem(node);
        }else{
            add_filesystem(node);
        }
    }
    function is_valid_filesystem(node){
        var node_filesystem = get_path_obj_from_path(node.data.fs_data.path).filesystem;
        if(!current_filesystem){
            current_filesystem = node_filesystem;
            return true;
        }
        return current_filesystem == node_filesystem;
    }
    function add_request(node) {
        var request_id = node.data.fs_data.req_index;
        batch_list.push(request_id);
        add_marked_style_to_node(node);
    }
    function remove_request(node) {
        var request_id = node.data.fs_data.req_index;
        batch_list = batch_list.filter(function (id) {
            return id != request_id;
        });
        remove_marked_style_from_node(node);
    }
    function add_test(node) {
        var test_id = node.data.fs_data.test_index;
        batch_list.push(test_id);
        add_marked_style_to_node(node);
    }
    function remove_test(node) {
        var test_id = node.data.fs_data.test_index;
        batch_list = batch_list.filter(function (id) {
            return id != test_id;
        });
        remove_marked_style_from_node(node);
    }
    function add_package(node) {
        var node_path = node.data.fs_data.path;
        var path_obj = get_path_obj_from_path(node_path);
        var package_name = path_obj.package;
        batch_list.push(package_name);
        add_marked_style_to_node(node);
    }
    function remove_package(node) {
        var node_path = node.data.fs_data.path;
        var path_obj = get_path_obj_from_path(node_path);
        var package_name = path_obj.package;
        batch_list = batch_list.filter(function (name) {
            return name != package_name;
        });
        remove_marked_style_from_node(node);
    }
    function add_filesystem(node) {
        var node_path = node.data.fs_data.path;
        var path_obj = get_path_obj_from_path(node_path);
        var filesystem_name = path_obj.filesystem;
        batch_list.push(filesystem_name);
        add_marked_style_to_node(node);
    }
    function remove_filesystem(node) {
        var node_path = node.data.fs_data.path;
        var path_obj = get_path_obj_from_path(node_path);
        var filesystem_name = path_obj.filesystem;
        batch_list = batch_list.filter(function (name) {
            return name != filesystem_name;
        });
        remove_marked_style_from_node(node);
    }
    function add_marked_style_to_node(node) {
        node.addClass(MARKED_STYLE);
    }
    function remove_marked_style_from_node(node) {
        node.removeClass(MARKED_STYLE);
    }
    this.reset_batch = function (tree) {
        batch_type = "";
        batch_list = [];
        current_filesystem = "";
        if(tree){
            tree.findAll(remove_marked_style_from_node);
        }
    }
    this.reset_batch = this.reset_batch.bind(this);
    this.get_batch_type = function () {
        return batch_type;
    }
    this.get_batch_type = this.get_batch_type.bind(this);
    this.get_formatted_data = function () {
        data = {};
        switch (batch_type){
            case "request":
                data.filesystem = current_filesystem;
                data.requests = batch_list;
                break;
            case "test":
                data.filesystem = current_filesystem;
                data.tests = batch_list;
                break;
            case 'package':
                data.filesystem = current_filesystem;
                data.packages = batch_list;
                break;
            case 'filesystem':
                data.filesystems = batch_list;
                break;
        }
        return data;
    }
    this.get_formatted_data = this.get_formatted_data.bind(this);
    this.stash = function (tree) {
        stashed_batch_type = batch_type;
        stashed_batch_filesystem = current_filesystem;
        stashsed_batch_list = batch_list;
        this.reset_batch(tree)
    }
    this.stash = this.stash.bind(this);
    this.has_stash = function () {
        return !!stashed_batch_type;
    }
    this.has_stash = this.has_stash.bind(this);
    this.clean_stash = function () {
        stashed_batch_type = "";
        stashed_batch_filesystem = "";
        stashsed_batch_list = [];
    }
    this.clean_stash = this.clean_stash.bind(this);
    this.get_formatted_stashed_data = function () {
        data = {};
        switch (stashed_batch_type){
            case "request":
                data.filesystem = stashed_batch_filesystem;
                data.requests = stashsed_batch_list;
                break;
            case "test":
                data.filesystem = stashed_batch_filesystem;
                data.tests = stashsed_batch_list;
                break;
            case 'package':
                data.filesystem = stashed_batch_filesystem;
                data.packages = stashsed_batch_list;
                break;
            case 'filesystem':
                data.filesystems = stashsed_batch_list;
                break;
        }
        return data;
    }
    this.get_formatted_stashed_data = this.get_formatted_stashed_data.bind(this);
    this.get_stash_batch_type = function () {
        return stashed_batch_type;
    }
    this.get_stash_batch_type = this.get_stash_batch_type.bind(this);
}

var tree_expand;
var comp;
var name_input;
var data;
var ctrl_watcher;
var cmd_watcher;
var batch;

var cut_path = "";
var cut_type = "";


$(document).ready(function () {
    ctrl_watcher = new key_watcher(17);
    cmd_watcher =  new key_watcher(91);
    $.get('directory',null,function(data){
        loadFancyTree("#tree", prepareFancyTreeData(data));
    }, "json");
    loadTestResultTree("#test-tree",[]);
    comp = new compare_panel("#compare-panel");
    name_input = new name_panel("#name-panel");
    data = new data_panel('#data-panel');
    tree_expand = new expand_container('#tree');
    batch = new batch_clipboard();
    $('#cred-save').click(function(){
        var app_name = $('#app-name').val();
        var client_id = $('#client-id').val();
        var client_secret = $('#client-secret').val();
        $.get('/cred', {app_name, client_id, client_secret}, function(data){console.log(data)})
    });
    $.get('/cred/get', {} , function(data){
        $('#app-name').val(data.appname);
        $('#client-id').val(data.client_id);
        $('#client-secret').val(data.client_secret);
    }, 'json')
});

function onCompareClicked(e) {
    e.preventDefault();
    var target = e.target;
    var path = target.dataset.node;
    var tree = $('#test-tree').fancytree('getTree');
    var node = tree.getNodeByKey(path);
    var actual = node.data.fs_data.actual;
    var expected = node.data.fs_data.expected;
    console.log(tree.getNodeByKey('status:'));
    console.log(node);
    comp.show_compare(expected,actual);
}

function onDataClicked(e) {
    console.log(e);
    var target_button = $(e.target);
    var request_data = target_button.data('request_data');
    var request_name = target_button.data('request_name');
    data.show_data(request_name, request_data);
}

function onRenameClicked(e) {
    var node = $(e.target).data('node');
    renameNode(node);
}

function onMoveUp(e) {
    var node = $(e.target).data('node');
    move_up(node);
}

function onMoveDown(e) {
    var node = $(e.target).data('node');
    move_down(node);
}

function loadFancyTree(id,source) {
    $(id).fancytree({
        checkbox: true,
        source: source,
        titlesTabbable: true, // Add all node titles to TAB chain
        quicksearch: true, // Jump to nodes when pressing first character
        extensions: ["table","glyph"],
        table: {
            indentation: 20,
            nodeColumnIdx: 3,
            checkboxColumnIdx: 0,
        },
        createNode: function(event, data){
            var node = data.node;
            var $tdList = $(node.tr).find(">td");
            node.addClass('context-node');
            node.addClass('context-node-'+node.data.fs_data.type);
            if(node.isFolder()){
                if(node.data.fs_data.type == 'filesystem'){
                    node.checkbox = false;
                    $tdList.eq(0).remove();
                    $tdList.eq(3).prop("colspan", 8).nextAll().remove();
                }
                else if(node.data.fs_data.type == 'test'){
                    $tdList.eq(2).remove();
                    $tdList.eq(3).prop("colspan", 3);
                    $tdList.eq(4).prop("colspan", 5).nextAll().remove();
                }else{
                    $tdList.eq(3).prop("colspan", 7).nextAll().remove();
                }
                if(node.data.fs_data.type != 'test'){
                    $tdList.eq(1).remove();
                    $tdList.eq(2).remove();
                }
            }
            if(node.data.fs_data.type != 'filesystem') node.setSelected(!!node.data.fs_data.selected)
            if(node.data.fs_data.type == 'request'){
                if(node.data.fs_data.req_status == 'SUCCESS') node.addClass('success-background');
                else if(node.data.fs_data.req_status == 'ERROR') node.addClass('error-background');
                else if(node.data.fs_data.req_content_type == 'json') node.addClass('json-background');
                else node.addClass('others-background');
            }
        },
        renderColumns: function (event, data) {
            var node = data.node,
                $tdList = $(node.tr).find(">td");
            $tdList.eq(1).text(node.data.fs_data.req_method || '');
            if(node.data.fs_data.type == 'test') {
                $tdList.eq(1).text(node.data.fs_data.test_index || '')
                $tdList.eq(1).addClass('test-index');
                $tdList.eq(4).append('<button class="rename-button">Rename</button>');
                $tdList.eq(4).append('<button class="up-button">Move Up</button>');
                $tdList.eq(4).append('<button class="down-button">Move down</button>');
                $tdList.eq(4).find('.rename-button').data('node',node).click(onRenameClicked);
                $tdList.eq(4).find('.up-button').data('node',node).click(onMoveUp);
                $tdList.eq(4).find('.down-button').data('node',node).click(onMoveDown);
            }
            if(node.data.fs_data.type == 'request'){
                $tdList.eq(2).text(node.data.fs_data.req_index || '');
                $tdList.eq(2).addClass('test-index');
                $tdList.eq(4).text(node.data.fs_data.req_path || '');
                $tdList.eq(5).append('<button class="data-button">view data</button>')
                    .find('button')
                    .data('request_data', node.data.fs_data.req_data)
                    .data('request_name', node.title)
                    .click(onDataClicked);
                $tdList.eq(6).text(node.data.fs_data.req_status_code || '');
                $tdList.eq(7).text(node.data.fs_data.req_content_type || '');
            }
            $tdList.data('key', node.key)

        },
        beforeSelect: function(event, data){
            var node = data.node;
            var path = node.data.fs_data.path;
            var type = node.data.fs_data.type;
            var path_obj = get_path_obj_from_path(path);
            if(type == 'test'){
                var data = {
                    filesystem: path_obj.filesystem,
                    package_path: path_obj.package,
                    test_no: path_obj.test_case,
                    selected: (!node.isSelected())?'selected': null,
                }
                $.get('test/select', data, function (data) {
                    //console.log(data);
                }, "json").fail(function (error) {
                    console.log(error);
                    //FlashMessage("Some Error occurred. Check the console");
                });
            }else if(type == 'request'){
                var data = {
                    filesystem: path_obj.filesystem,
                    package_path: path_obj.package,
                    test_no: path_obj.test_case,
                    request_no: path_obj.request,
                    selected: (!node.isSelected())?'selected': null,
                }
                $.get('request/select', data, function (data) {
                    //console.log(data);
                }, "json").fail(function (error) {
                    console.log(error);
                    //FlashMessage("Some Error occurred. Check the console");
                });
            }
            else if(type == 'package'){
                var data = {
                    filesystem: path_obj.filesystem,
                    package_path: path_obj.package,
                    selected: (!node.isSelected())?'selected': null,
                }
                $.get('package/select', data, function (data) {
                    //console.log(data);
                }, "json").fail(function (error) {
                    console.log(error);
                    //FlashMessage("Some Error occurred. Check the console");
                });
            }
            return true;
        },
        glyph: {
            preset: "awesome4",
            map: {
            }
        },
        click: function (e, data) {
            var node = data.node;
            var tree = data.tree;
            if(ctrl_watcher.is_pressed() || cmd_watcher.is_pressed()){
                batch.toggle_node_in_batch(node);
            }
            else{
                batch.reset_batch(tree);
            }
        }
    });
    var context_menu_items = {
        play: {
            name: 'Play',
            disabled: function (itemKey, opt) {
                var dir_type = this[0].ftnode.data.fs_data.type;
                if(dir_type == 'request' || dir_type == 'test') return true;
                return false;
            }
        },
        rename : {
            name: "Rename",
            disabled: function (itemKey, opt) {
                return !is_rename_allowed(opt.$trigger[0].ftnode);
            }
        },
        cut: {
            name: "Cut",
            disabled: function (itemKey, opt) {
                return !is_cut_allowed(opt.$trigger[0].ftnode);
            }
        },
        paste :{
            name: "Paste",
            disabled: function (itemKey, opt) {
                return !is_paste_allowed(opt.$trigger[0].ftnode);
            }
        },
        move_up :{
            name: "Move up",
            disabled: function (itemKey, opt) {
                return !is_move_allowed(opt.$trigger[0].ftnode);
            }
        },
        move_down :{
            name: "Move down",
            disabled: function (itemKey, opt) {
                return !is_move_allowed(opt.$trigger[0].ftnode);
            }
        },
        create :{
            name: "Create",
            disabled: function (itemKey, opt) {
                var dir_type = opt.$trigger[0].ftnode.data.fs_data.type;
                if(dir_type != "package") return true;
                return false;
            },
            items : {
                new_package : {
                    name: "New Package", disabled: function (itemKey, opt) {
                        var dir_type = opt.$trigger[0].ftnode.data.fs_data.type;
                        if(dir_type != "package" && dir_type != "filesystem") return true;
                        return false;
                    },
                },
                new_test : {
                    name: "New Test Case", disabled: function (itemKey, opt) {
                        var dir_type = opt.$trigger[0].ftnode.data.fs_data.type;
                        if(dir_type != "package") return true;
                        return false;
                    },
                },
            }
        },
        delete :{
            name: "Delete",
            disabled: function (itemKey, opt) {
                return !is_delete_allowed(opt.$trigger[0].ftnode);
            },
        },
        status :{
            name: "Set Status",
            disabled: function (itemKey, opt) {
                var dir_type = opt.$trigger[0].ftnode.data.fs_data.type;
                if(dir_type != "request") return true;
                return false;
            },
            items: {
                status_ok: {
                    name: "Ok",
                },
                status_success: {
                    name: "Success",
                },
                status_error: {
                    name: "Error",
                }
            }
        },
        check_all: {
            name: "Check all",
            disabled: function (itemKey, opt) {
                // var dir_type = opt.$trigger[0].ftnode.data.fs_data.type;
                // if(dir_type != "filesystem") return true;
                // return false;
                return false;
            },
        }
    }
    $('#tree').contextMenu({
        selector: '.context-node',
        items: context_menu_items,
        callback: function (itemKey, opt) {
            var nodepath = opt.$trigger[0].ftnode.data.fs_data.path;
            var nodetype = opt.$trigger[0].ftnode.data.fs_data.type;
            switch (itemKey){
                case "play":
                    var path_obj = get_path_obj_from_path(nodepath);
                    FlashMessage("Started Playing");
                    $.get('play',path_obj, function (data) {
                        console.log(data);
                        FlashMessage('Success');
                        var result_source = [prepareTestResultSource(data)];
                        var tree = $('#test-tree').fancytree('getTree');
                        tree.reload(result_source);
                    }, "json").fail(function (error) {
                        console.log(error);
                        FlashMessage("Some Error occurred. Check the console");
                    });
                    break;
                case 'cut':
                    cut(opt.$trigger[0].ftnode);
                    break;
                case 'paste':
                    paste(opt.$trigger[0].ftnode);
                    break;
                case 'move_up':
                    move_up(opt.$trigger[0].ftnode);
                    break;
                case 'move_down':
                    move_down(opt.$trigger[0].ftnode);
                    break;
                case 'rename':
                    renameNode(opt.$trigger[0].ftnode);
                    break;
                case 'new_package':
                    var func = function (name) {
                        var path_obj = get_path_obj_from_path(nodepath);
                        var path_data = {
                            filesystem: path_obj.filesystem,
                            package_path: path_obj.package,
                            package_name: name,
                        }
                        $.get('package/new',path_data, function (data) {
                            FlashMessage('Successfully created package ' + name);
                            $.get('directory',null,function(data){
                                var tree = $('#tree').fancytree('getTree')
                                tree_expand.storeExpand();
                                tree.reload(prepareFancyTreeData(data));
                                tree.activateKey(nodepath + '/' + name);
                                tree_expand.restoreExpand();
                            }, "json");
                        }, "json").fail(function (error) {
                            console.log(error);
                            FlashMessage("Some Error occurred. Check the console");
                        });
                    };
                    name_input.show_name("New Package", "Create", func);
                    break;
                case 'new_test':
                    var func = function (name) {
                        var path_obj = get_path_obj_from_path(nodepath);
                        var path_data = {
                            filesystem: path_obj.filesystem,
                            package_path: path_obj.package,
                            test_name: name,
                        }
                        $.get('test/new',path_data, function (data) {
                            FlashMessage('Successfully created test ' + name);
                            $.get('directory',null,function(data){
                                var tree = $('#tree').fancytree('getTree');
                                tree_expand.storeExpand();
                                tree.reload(prepareFancyTreeData(data));
                                tree.activateKey(nodepath);
                                tree.getActiveNode().findFirst(name).setActive(true);
                                tree_expand.restoreExpand();
                            }, "json");
                        }, "json").fail(function (error) {
                            console.log(error);
                            FlashMessage("Some Error occurred. Check the console");
                        });
                    };
                    name_input.show_name("New Test", "Create" , func);
                    break;
                case 'delete':
                    delete_node(opt.$trigger[0].ftnode);
                    break;
                case 'status_ok':
                    var path_obj = get_path_obj_from_path(nodepath);
                    var data = {
                        filesystem: path_obj.filesystem,
                        package_path: path_obj.package,
                        test_no: path_obj.test_case,
                        request_no: path_obj.request,
                        status: 'OK',
                    }
                    $.get('request/status',data, function (data) {
                        FlashMessage('Successfully set status');
                        $.get('directory',null,function(data){
                            var tree = $('#tree').fancytree('getTree');
                            tree_expand.storeExpand();
                            tree.reload(prepareFancyTreeData(data));
                            tree.activateKey(nodepath);
                            tree_expand.restoreExpand();
                        }, "json");
                    }, "json").fail(function (error) {
                        console.log(error);
                        FlashMessage("Some Error occurred. Check the console");
                    });
                    break;
                case 'status_success':
                    var path_obj = get_path_obj_from_path(nodepath);
                    var data = {
                        filesystem: path_obj.filesystem,
                        package_path: path_obj.package,
                        test_no: path_obj.test_case,
                        request_no: path_obj.request,
                        status: 'SUCCESS',
                    }
                    $.get('request/status',data, function (data) {
                        FlashMessage('Successfully set status');
                        $.get('directory',null,function(data){
                            var tree = $('#tree').fancytree('getTree');
                            tree_expand.storeExpand();
                            tree.reload(prepareFancyTreeData(data));
                            tree.activateKey(nodepath);
                            tree_expand.restoreExpand();
                        }, "json");
                    }, "json").fail(function (error) {
                        console.log(error);
                        FlashMessage("Some Error occurred. Check the console");
                    });
                    break;
                case 'status_error':
                    var path_obj = get_path_obj_from_path(nodepath);
                    var data = {
                        filesystem: path_obj.filesystem,
                        package_path: path_obj.package,
                        test_no: path_obj.test_case,
                        request_no: path_obj.request,
                        status: 'ERROR',
                    }
                    $.get('request/status',data, function (data) {
                        FlashMessage('Successfully set status');
                        $.get('directory',null,function(data){
                            var tree = $('#tree').fancytree('getTree');
                            tree_expand.storeExpand();
                            tree.reload(prepareFancyTreeData(data));
                            tree.activateKey(nodepath);
                            tree_expand.restoreExpand();
                        }, "json");
                    }, "json").fail(function (error) {
                        console.log(error);
                        FlashMessage("Some Error occurred. Check the console");
                    });
                    break;
                case 'check_all':
                    var node = opt.$trigger[0].ftnode;
                    check_node(node);
                    break;
            }
        }
    })
        .on("nodeCommand", function(event, data){
            var tree = $(this).fancytree("getTree");
            var node = tree.getActiveNode();
            switch (data.cmd){
                case "delete":
                    delete_node(node);
                    break;
                case 'rename':
                    renameNode(node);
                    break;
                case 'cut':
                    cut(node);
                    break;
                case 'paste':
                    paste(node);
                    break;
                case 'move_up':
                    move_up(node);
                    break;
                case 'move_down':
                    move_down(node);
                    break;
                case 'view_data':
                    view_data(node);
                    break;
            }
        })
        .on("keydown", function(e){
            var cmd = null;
            switch( $.ui.fancytree.eventToString(e) ) {
                case "del":
                    cmd = "delete";
                    break;
                case 'f2':
                    cmd = 'rename';
                    break;
                case 'ctrl+x':
                    cmd = 'cut';
                    break;
                case 'ctrl+v':
                    cmd = 'paste';
                    break;
                case 'ctrl+up':
                    cmd = 'move_up';
                    break;
                case 'ctrl+down':
                    cmd = 'move_down';
                    break;
                case 'return':
                    cmd = 'view_data';
                    break;
            }
            if(cmd){
                $(this).trigger("nodeCommand", {cmd: cmd});
                return false;
            }
        })
}

var flash_timeout;

function FlashMessage(msg){
    $('#flash').text(msg).show(500,function(){
        clearTimeout(flash_timeout);
        flash_timeout = setTimeout(function () {
            $('#flash').hide(500);
        }, 3000);
    });
}

function get_path_obj_from_path(path){
    var path_obj = {};
    var tokens = path.split(':');
    path_obj.filesystem = tokens[0];
    if(tokens.length <= 1) return path_obj;
    tokens = tokens[1].split('|');
    path_obj.package = tokens[0];
    if(tokens.length > 1) path_obj.test_case = tokens[1];
    if(tokens.length > 2) path_obj.request = tokens[2];
    return path_obj;
}

function prepareFancyTreeData(source){
    var ret = [];
    for(var fs in source){
        var path = source[fs].name + ':';
        var _new = {
            title: source[fs].name,
            key: path,
            fs_data:{
                type: 'filesystem',
                name: source[fs].name,
                path: path,
            },
            checkbox: false, folder: true, icon: 'fa fa-book'
        }
        //console.log(source);
        _new.children = [prepareFancyTreePackage(source[fs].test_file.packages[0], path, 0)];
        ret.push(_new);
    }
    return ret;
}

function prepareFancyTreePackage(package, path, index) {
    path = path + '/' + package.dir;
    var ret_pck = {
        title: package.dir, key: path, fs_data:{
            type: 'package',
            name: package.dir,
            path: path,
            index: index,
            selected: package.selected,
        },
        folder: true,
    };
    var child_pcks = [];
    var child_packages = package.packages;
    for(var pck in child_packages){
        var _new = prepareFancyTreePackage(child_packages[pck], path, pck)
        child_pcks.push(_new);
    }
    var child_tests = package.test_cases;
    var ret_tests = [];
    for(var test in child_tests){
        ret_tests.push(prepareFancyTreeTest(child_tests[test], path, test))
    }
    ret_pck.children = child_pcks.concat(ret_tests);
    return ret_pck;
}

function prepareFancyTreeTest(test, path, index){
    path = path + '|' + index;
    var ret = {
        title: test.name, key: path, fs_data:{
            type: 'test',
            name: test.name,
            path: path,
            index: index,
            selected: test.selected,
            test_index: test.index.toString(),
        }, folder: true, icon: 'fa fa-tags',
    };
    var child_reqs = test.requests;
    var ret_reqs = [];
    for(var req in child_reqs){
        ret_reqs.push(prepareFancyTreeRequest(child_reqs[req], path, req));
    }
    ret.children = ret_reqs;
    return ret;
}

function prepareFancyTreeRequest(request, path, index){
    path = path + '|' + index;
    var content_type;
    if(request.content_type.toLowerCase().includes('html')) content_type = 'html';
    else if(request.content_type.toLowerCase().includes('json')) content_type = 'json';
    else content_type = request.content_type;
    var ret = {
        title: request.name, key: path, fs_data:{
            type: 'request',
            name: request.name,
            path: path,
            index: index,
            selected: request.selected,
            req_path: request.path,
            req_method: request.method,
            req_status_code: request.status_code,
            req_content_type: content_type,
            req_status: request.status,
            req_index: request.index.toString(),
            req_data: request.data,
        }
    };
    return ret;
}

function loadTestResultTree(id, source) {
    $(id).fancytree({
        checkbox: false,
        source: source,
        titlesTabbable: true, // Add all node titles to TAB chain
        quicksearch: true, // Jump to nodes when pressing first character

        extensions: ["table", "glyph"],
        table: {
            indentation: 20,
            nodeColumnIdx: 1,
        },
        createNode: function(event, data){
            var node = data.node;
            var $tdList = $(node.tr).find(">td");
            if(node.isFolder() || node.data.skipped) {
                $tdList.eq(1).prop('colspan', 2).nextAll().remove();
            }
            if(node.data.fs_data == undefined){
                // do nothing
            }
            else if(node.data.fs_data.success){
                node.addClass('success-background');
            }else{
                node.addClass('error-background');
            }
        },
        renderColumns: function (event, data) {
            var node = data.node,
                $tdList = $(node.tr).find(">td");
            if(node.data.fs_data){
                var td = $tdList.eq(2);
                td.append('<button data-node='+'"'+ node.data.fs_data.path +'"'+'>compare</button>')
                    .click(onCompareClicked);
                var index = node.data.fs_data.index;
                var nodetype = node.data.fs_data.type;
                if(index != undefined && index != null && nodetype != 'package'){
                    $tdList.eq(0).text(index);
                }
            }
        },
        glyph: {
            preset: "awesome4",
            map: {
            }
        },
    });
}

function prepareTestResultSource(source) {
    var path = source.filesystem + ':';
    var _new = {
        title: source.filesystem,
        key: path,
        fs_data:{
            type: 'filesystem',
            name: source.filesystem,
            path: path,
            success: source.success,
        },
        folder: true,
    }
    _new.children = [prepareTestResultPackage(source.packages[0], path, 0)];
    return _new;
}

function prepareTestResultPackage(package, path, index) {
    if(package == null || package == undefined){
        return {
            title: 'skipped', skipped: true,
        }
    }
    path = path + '/' + package.dir;
    var ret_pck = {
        title: package.dir, key: path, fs_data:{
            type: 'package',
            name: package.dir,
            path: path,
            index: index,
            selected: package.selected,
            success: package.success,
        },
        folder: true
    };
    var child_pcks = [];
    var child_packages = package.packages;
    for(var pck in child_packages){
        var packages = prepareTestResultPackage(child_packages[pck], path, pck)
        var _new = packages
        child_pcks.push(_new);
    }
    var child_tests = package.test_cases;
    var ret_tests = [];
    for(var test in child_tests){
        ret_tests.push(prepareTestResultTests(child_tests[test], path, test))
    }
    ret_pck.children = child_pcks.concat(ret_tests);
    return ret_pck;
}

function prepareTestResultTests(test, path, index){
    path = path + '|' + index;
    if(test == null){
        return {
            title: 'skipped', skipped: true,
        }
    }
    var ret = {
        title: test.name, key: path, fs_data:{
            type: 'test',
            name: test.name,
            path: path,
            index: index,
            selected: test.selected,
            success: test.success,
        }, folder: true,
    };
    var child_reqs = test.requests;
    var ret_reqs = [];
    for(var req in child_reqs){
        ret_reqs.push(prepareTestResultRequests(child_reqs[req], path, req));
    }
    ret.children = ret_reqs;
    return ret;
}

function prepareTestResultRequests(request, path, index) {
    if(request == null) {
        return {
            title: 'skipped', skipped: true,
        }
    }
    path = path + '|' + index;
    var ret = {
        title: request.name, key: path, fs_data:{
            type: 'request',
            name: request.name,
            path: path,
            index: index,
            success: request.success,
            expected: request.expected,
            actual: request.actual,
        }
    };
    return ret;
}

function set_tree_focus() {
    $('#tree').fancytree('getActiveNode').setFocus(true);
}

function renameNode(node) {
    if(!is_rename_allowed(node)) return;
    var nodepath = node.data.fs_data.path;
    var nodetype = node.data.fs_data.type;
    var path_obj = get_path_obj_from_path(nodepath);
    var name = node.title;
    if(nodetype == 'package') {
        name_input.show_name(name, 'Rename', function (name) {
            var parent = path_obj.package.split('/');
            parent.pop();
            parent = parent.join('/');
            var data = {
                filesystem: path_obj.filesystem,
                package_path: path_obj.package,
                package_name: name,
            };
            $.get('package/rename',data, function (data) {
                FlashMessage('Successfully renamed');
                $.get('directory',null,function(data){
                    var tree = $('#tree').fancytree('getTree');
                    tree_expand.storeExpand();
                    tree.reload(prepareFancyTreeData(data));
                    tree.activateKey(path_obj.filesystem+ ':' + parent + '/' +name);
                    tree_expand.restoreExpand();
                }, "json");
            }, "json").fail(function (error) {
                console.log(error);
                FlashMessage("Some Error occurred. Check the console");
            });
        });
    }else if(nodetype == 'test') {
        name_input.show_name(name, 'Rename', function (name) {
            var data = {
                filesystem: path_obj.filesystem,
                package_path: path_obj.package,
                test_no: path_obj.test_case,
                test_name: name,
            };
            $.get('test/rename',data, function (data) {
                FlashMessage('Successfully renamed');
                $.get('directory',null,function(data){
                    var tree = $('#tree').fancytree('getTree');
                    tree_expand.storeExpand();
                    tree.reload(prepareFancyTreeData(data));
                    tree.activateKey(nodepath);
                    tree_expand.restoreExpand();
                }, "json");
            }, "json").fail(function (error) {
                console.log(error);
                FlashMessage("Some Error occurred. Check the console");
            });
        });
    }else if(nodetype == 'request'){
        name_input.show_name(name, "Rename", function (name) {
            var data = {
                filesystem: path_obj.filesystem,
                package_path: path_obj.package,
                test_no: path_obj.test_case,
                request_no: path_obj.request,
                request_name: name,
            };
            $.get('request/rename',data, function (data) {
                FlashMessage('Successfully renamed');
                $.get('directory',null,function(data){
                    var tree = $('#tree').fancytree('getTree');
                    tree_expand.storeExpand();
                    tree.reload(prepareFancyTreeData(data));
                    tree.activateKey(nodepath);
                    tree_expand.restoreExpand();
                }, "json");
            }, "json").fail(function (error) {
                console.log(error);
                FlashMessage("Some Error occurred. Check the console");
            });
        });
    }
}

function move_up(node) {
    if(!is_move_allowed(node)) return;
    var nodepath = node.data.fs_data.path;
    var nodetype = node.data.fs_data.type;
    var path_obj = get_path_obj_from_path(nodepath);
    if(nodetype == 'test'){
        var path_data = {
            filesystem: path_obj.filesystem,
            package_path: path_obj.package,
            test_no: path_obj.test_case,
        }
        $.get('test/move_up',path_data, function (data) {
            //FlashMessage('Successfully moved up');
            $.get('directory',null,function(data){
                var tree = $('#tree').fancytree('getTree');
                var target_path = path_obj.filesystem+":"+path_obj.package+"|"+(Number(path_data.test_no)-1);
                tree_expand.storeExpand();
                tree_expand.swap(nodepath, target_path);
                tree.reload(prepareFancyTreeData(data));
                tree.activateKey(target_path);
                tree_expand.restoreExpand();
            }, "json");
        }, "json").fail(function (error) {
            console.log(error);
            FlashMessage("Some Error occurred. Check the console");
        });
    }
    else if(nodetype == 'package') {
        var parent = path_obj.package.split('/');
        parent.pop();
        parent = parent.join('/');
        var package_no = $('#tree').fancytree('getTree').findFirst(function (node) {
            if(node.key == nodepath) return true;
            return false;
        }).data.fs_data.index;
        var path_data = {
            filesystem: path_obj.filesystem,
            package_path: parent,
            package_no: package_no,
        };
        $.get('package/move_up',path_data, function (data) {
            FlashMessage('Successfully moved');
            $.get('directory',null,function(data){
                var tree = $('#tree').fancytree('getTree');
                tree_expand.storeExpand();
                tree.reload(prepareFancyTreeData(data));
                tree.activateKey(nodepath);
                tree_expand.restoreExpand();
            }, "json");
        }, "json").fail(function (error) {
            console.log(error);
            FlashMessage("Some Error occurred. Check the console");
        });
    }
    else if(nodetype == 'request'){
        var path_data = {
            filesystem: path_obj.filesystem,
            package_path: path_obj.package,
            test_no: path_obj.test_case,
            request_no: path_obj.request,
        }
        $.get('request/move_up',path_data, function (data) {
            FlashMessage('Successfully moved up');
            $.get('directory',null,function(data){
                var tree = $('#tree').fancytree('getTree');
                tree_expand.storeExpand();
                tree.reload(prepareFancyTreeData(data));
                tree.activateKey(
                    path_obj.filesystem+":"+path_obj.package+"|"+(Number(path_obj.test_case)+'|'+(Number(path_obj.request)-1))
                );
                tree_expand.restoreExpand();
            }, "json");
        }, "json").fail(function (error) {
            console.log(error);
            FlashMessage("Some Error occurred. Check the console");
        });
    }
}

function move_down(node) {
    if(!is_move_allowed(node)) return;
    var nodepath = node.data.fs_data.path;
    var nodetype = node.data.fs_data.type;
    var path_obj = get_path_obj_from_path(nodepath);
    if(nodetype == 'test'){
        var path_data = {
            filesystem: path_obj.filesystem,
            package_path: path_obj.package,
            test_no: path_obj.test_case,
        }
        $.get('test/move_down',path_data, function (data) {
            //FlashMessage('Successfully moved up');
            $.get('directory',null,function(data){
                var tree = $('#tree').fancytree('getTree');
                var target_path = path_obj.filesystem+":"+path_obj.package+"|"+(Number(path_data.test_no)+1);
                tree_expand.storeExpand();
                tree_expand.swap(nodepath, target_path);
                tree.reload(prepareFancyTreeData(data));
                tree.activateKey(target_path);
                tree_expand.restoreExpand();
            }, "json");
        }, "json").fail(function (error) {
            console.log(error);
            FlashMessage("Some Error occurred. Check the console");
        });
    }else if(nodetype == 'package'){
        var parent = path_obj.package.split('/');
        parent.pop();
        parent = parent.join('/');
        var package_no = $('#tree').fancytree('getTree').findFirst(function (node) {
            if(node.key == nodepath) return true;
            return false;
        }).data.fs_data.index;
        var path_data = {
            filesystem: path_obj.filesystem,
            package_path: parent,
            package_no: package_no,
        };
        $.get('package/move_down',path_data, function (data) {
            //FlashMessage('Successfully moved');
            $.get('directory',null,function(data){
                var tree = $('#tree').fancytree('getTree');
                tree_expand.storeExpand();
                tree.reload(prepareFancyTreeData(data));
                tree.activateKey(nodepath)
                tree_expand.restoreExpand();
            }, "json");
        }, "json").fail(function (error) {
            console.log(error);
            FlashMessage("Some Error occurred. Check the console");
        });
    }else if(nodetype == 'request'){
        var path_data = {
            filesystem: path_obj.filesystem,
            package_path: path_obj.package,
            test_no: path_obj.test_case,
            request_no: path_obj.request,
        }
        $.get('request/move_down',path_data, function (data) {
            //FlashMessage('Successfully moved up');
            $.get('directory',null,function(data){
                var tree = $('#tree').fancytree('getTree');
                tree_expand.storeExpand();
                tree.reload(prepareFancyTreeData(data));
                tree.activateKey(
                    path_obj.filesystem+":"+path_obj.package+"|"+(Number(path_obj.test_case)+'|'+(Number(path_obj.request)+1))
                );
                tree_expand.restoreExpand();
            }, "json");
        }, "json").fail(function (error) {
            console.log(error);
            FlashMessage("Some Error occurred. Check the console");
        });
    }
}

function delete_node(node) {
    if(!batch.is_empty()){
        switch(batch.get_batch_type()){
            case 'request':
                var data = batch.get_formatted_data();
                $.get('/request/delete/batch', data, function (data) {
                    FlashMessage('Successfully deleted marked requests');
                    console.log(data);
                    $.get('directory',null,function(data){
                        var tree = $('#tree').fancytree('getTree');
                        tree_expand.storeExpand();
                        tree.reload(prepareFancyTreeData(data));
                        tree_expand.restoreExpand();
                    }, "json");
                }, "json").fail(function (error) {
                    console.log(error);
                    FlashMessage("Some Error occurred. Check the console");
                });
                break;
            case 'test':
                var data = batch.get_formatted_data();
                $.get('/test/delete/batch', data, function (data) {
                    FlashMessage('Successfully deleted marked tests');
                    console.log(data);
                    $.get('directory',null,function(data){
                        var tree = $('#tree').fancytree('getTree');
                        tree_expand.storeExpand();
                        tree.reload(prepareFancyTreeData(data));
                        tree_expand.restoreExpand();
                    }, "json");
                }, "json").fail(function (error) {
                    console.log(error);
                    FlashMessage("Some Error occurred. Check the console");
                });
                break;
            case 'package':
                var data = batch.get_formatted_data();
                $.get('/package/delete/batch', data, function (data) {
                    FlashMessage('Successfully deleted marked packages');
                    console.log(data);
                    $.get('directory',null,function(data){
                        var tree = $('#tree').fancytree('getTree');
                        tree_expand.storeExpand();
                        tree.reload(prepareFancyTreeData(data));
                        tree_expand.restoreExpand();
                    }, "json");
                }, "json").fail(function (error) {
                    console.log(error);
                    FlashMessage("Some Error occurred. Check the console");
                });
                break;
            case 'filesystem':
                var data = batch.get_formatted_data();
                $.get('/filesystem/delete/batch', data, function (data) {
                    FlashMessage('Successfully deleted marked filesystems');
                    console.log(data);
                    $.get('directory',null,function(data){
                        var tree = $('#tree').fancytree('getTree');
                        tree_expand.storeExpand();
                        tree.reload(prepareFancyTreeData(data));
                        tree_expand.restoreExpand();
                    }, "json");
                }, "json").fail(function (error) {
                    console.log(error);
                    FlashMessage("Some Error occurred. Check the console");
                });
                break;
        }
        batch.reset_batch();
        return;
    }
    if(!is_delete_allowed(node)) return;
    var nodepath = node.data.fs_data.path;
    var nodetype = node.data.fs_data.type;
    var path_obj = get_path_obj_from_path(nodepath);
    if(nodetype == 'test'){
        var path_data = {
            filesystem: path_obj.filesystem,
            package_path: path_obj.package,
            test_no: path_obj.test_case,
        }
        $.get('test/delete',path_data, function (data) {
            FlashMessage('Successfully deleted');
            $.get('directory',null,function(data){
                var tree = $('#tree').fancytree('getTree');
                tree_expand.storeExpand();
                tree.reload(prepareFancyTreeData(data));
                tree.activateKey(path_obj.filesystem+":"+path_obj.package);
                tree.getActiveNode().setExpanded(true);
                tree_expand.restoreExpand();
            }, "json");
        }, "json").fail(function (error) {
            console.log(error);
            FlashMessage("Some Error occurred. Check the console");
        });
    }
    else if(nodetype == 'package') {
        var parent = path_obj.package.split('/');
        parent.pop();
        parent = parent.join('/');
        var package_no = $('#tree').fancytree('getTree').findFirst(function (node) {
            if(node.key == nodepath) return true;
            return false;
        }).data.fs_data.index;
        var path_data = {
            filesystem: path_obj.filesystem,
            package_path: parent,
            package_no: package_no,
        };
        $.get('package/delete',path_data, function (data) {
            FlashMessage('Successfully deleted package');
            $.get('directory',null,function(data){
                var tree = $('#tree').fancytree('getTree');
                tree_expand.storeExpand();
                tree.reload(prepareFancyTreeData(data));
                tree.activateKey(path_obj.filesystem+":"+parent);
                tree.getActiveNode().setExpanded(true);
                tree_expand.restoreExpand();
            }, "json");
        }, "json").fail(function (error) {
            console.log(error);
            FlashMessage("Some Error occurred. Check the console");
        });
    }
    else if(nodetype == 'request'){
        var path_data = {
            filesystem: path_obj.filesystem,
            package_path: path_obj.package,
            test_no: path_obj.test_case,
            request_no: path_obj.request,
        }
        $.get('request/delete',path_data, function (data) {
            FlashMessage('Successfully deleted');
            $.get('directory',null,function(data){
                var tree = $('#tree').fancytree('getTree');
                tree_expand.storeExpand();
                tree.reload(prepareFancyTreeData(data));
                tree.activateKey(path_obj.filesystem+":"+path_obj.package + '|' + path_obj.test_case);
                tree.getActiveNode().setExpanded(true);
                tree_expand.restoreExpand();
            }, "json");
        }, "json").fail(function (error) {
            console.log(error);
            FlashMessage("Some Error occurred. Check the console");
        });
    }
    else if(nodetype == 'filesystem'){
        var path_data = {
            filesystem: path_obj.filesystem,
        }
        $.get('filesystem/delete',path_data, function (data) {
            FlashMessage('Successfully deleted filesystem');
            $.get('directory',null,function(data){
                var tree = $('#tree').fancytree('getTree');
                tree_expand.storeExpand();
                tree.reload(prepareFancyTreeData(data));
                tree_expand.restoreExpand();
            }, "json");
        }, "json").fail(function (error) {
            console.log(error);
            FlashMessage("Some Error occurred. Check the console");
        });
    }
}

function is_delete_allowed(node) {
    var dir_type = node.data.fs_data.type;
    if(dir_type == "package"){
        var name = node.data.fs_data.name;
        if(name == 'root') return false;
    }
    return true;
}

function is_rename_allowed(node) {
    var dir_type = node.data.fs_data.type;
    if(dir_type == 'filesystem') return false;
    if(dir_type == 'package' && node.title == 'root') return false;
    return true;
}

function is_cut_allowed(node) {
    var dir_type = node.data.fs_data.type;
    if(dir_type == 'filesystem' || (dir_type == 'package' && node.title == 'root')) return false;
    return true;
}

function is_paste_allowed(node){
    if(batch.has_stash()) return true;
    var dir_type = node.data.fs_data.type;
    if(!cut_path || dir_type == 'filesystem') return false;
    if(cut_type == 'request' && dir_type != 'test') return false;
    if(cut_type == 'test' && dir_type != 'package') return false;
    if(cut_type == 'package' && dir_type != 'package') return false;
    var cut_fs = get_path_obj_from_path(cut_path);
    var dir_fs = get_path_obj_from_path(node.key);
    if(cut_fs.filesystem != dir_fs.filesystem) return false;
    else if(cut_type != 'request' && cut_fs.package == dir_fs.package) return false;
    else if(cut_type == 'request'){
        if(cut_fs.package == dir_fs.package && cut_fs.test_case == dir_fs.test_case) return false;
    }
    return true;
}

function is_move_allowed(node) {
    var dir_type = node.data.fs_data.type;
    if(dir_type == "filesystem" || (dir_type == 'package' && node.title == 'root')) return false;
    return true;
}

function cut(node) {
    if(!batch.is_empty()){
        batch.stash(node.tree);
        console.log(batch.get_formatted_stashed_data())
        return;
    }
    if(!is_cut_allowed(node)) return;
    console.log(batch.get_formatted_stashed_data())
    if(batch.has_stash()) batch.clean_stash();
    console.log(batch.get_formatted_stashed_data())
    var nodepath = node.data.fs_data.path;
    var nodetype = node.data.fs_data.type;
    cut_path = nodepath;
    cut_type = nodetype;
}

function paste(node) {
    if(batch.has_stash()){
        var node_type = node.data.fs_data.type;
        switch(batch.get_stash_batch_type()){
            case 'request':
                if(node_type != 'test') break;
                var data = batch.get_formatted_stashed_data();
                data.to_test = node.data.fs_data.test_index;
                $.get('/request/move/batch', data, function (data) {
                    FlashMessage('Successfully moved marked requests');
                    console.log(data);
                    $.get('directory',null,function(data){
                        var tree = $('#tree').fancytree('getTree');
                        tree_expand.storeExpand();
                        tree.reload(prepareFancyTreeData(data));
                        tree_expand.restoreExpand();
                    }, "json");
                }, "json").fail(function (error) {
                    console.log(error);
                    FlashMessage("Some Error occurred. Check the console");
                });
                break;
            case 'test':
                if(node_type != 'package') break;
                var data = batch.get_formatted_stashed_data();
                var path_obj = get_path_obj_from_path(node.data.fs_data.path);
                data.to_package = path_obj.package;
                $.get('/test/move/batch', data, function (data) {
                    FlashMessage('Successfully moved marked tests');
                    console.log(data);
                    $.get('directory',null,function(data){
                        var tree = $('#tree').fancytree('getTree');
                        tree_expand.storeExpand();
                        tree.reload(prepareFancyTreeData(data));
                        tree_expand.restoreExpand();
                    }, "json");
                }, "json").fail(function (error) {
                    console.log(error);
                    FlashMessage("Some Error occurred. Check the console");
                });
                break;
            case 'package':
                if(node_type != 'package') break;
                var data = batch.get_formatted_stashed_data();
                var path_obj = get_path_obj_from_path(node.data.fs_data.path);
                data.to_package = path_obj.package;
                $.get('/package/move/batch', data, function (data) {
                    FlashMessage('Successfully moved marked packages');
                    console.log(data);
                    $.get('directory',null,function(data){
                        var tree = $('#tree').fancytree('getTree');
                        tree_expand.storeExpand();
                        tree.reload(prepareFancyTreeData(data));
                        tree_expand.restoreExpand();
                    }, "json");
                }, "json").fail(function (error) {
                    console.log(error);
                    FlashMessage("Some Error occurred. Check the console");
                });
                break;
        }
        batch.clean_stash();
        return;
    }
    if(!is_paste_allowed(node)) return;
    var nodepath = node.data.fs_data.path;
    var from_path = get_path_obj_from_path(cut_path);
    var to_path = get_path_obj_from_path(nodepath);
    if(from_path.filesystem != to_path.filesystem) return;
    if(cut_type == 'test'){
        var path_data = {
            filesystem: from_path.filesystem,
            from_package: from_path.package,
            to_package: to_path.package,
            test_no: from_path.test_case,
        }
        $.get('test/move',path_data, function (data) {
            FlashMessage('Successfully moved');
            $.get('directory',null,function(data){
                var tree = $('#tree').fancytree('getTree');
                tree_expand.storeExpand();
                tree.reload(prepareFancyTreeData(data));
                tree.activateKey(nodepath);
                tree.getActiveNode().setExpanded(true);
                tree_expand.restoreExpand();
                cut_path = "";
            }, "json");
        }, "json").fail(function (error) {
            console.log(error);
            FlashMessage("Some Error occurred. Check the console");
        });
    }else if(cut_type == 'package'){
        var parent = from_path.package.split('/');
        parent.pop();
        parent = parent.join('/');
        var package_no = $('#tree').fancytree('getTree').findFirst(function (node) {
            if(node.key == cut_path) return true;
            return false;
        }).data.fs_data.index;
        var path_data = {
            filesystem: from_path.filesystem,
            from_package: parent,
            to_package: to_path.package,
            package_no: package_no,
        }
        $.get('package/move',path_data, function (data) {
            FlashMessage('Successfully moved');
            $.get('directory',null,function(data){
                var tree = $('#tree').fancytree('getTree');
                tree_expand.storeExpand();
                tree.reload(prepareFancyTreeData(data));
                tree.activateKey(nodepath);
                tree.getActiveNode().setExpanded(true);
                tree_expand.restoreExpand();
            }, "json");
        }, "json").fail(function (error) {
            console.log(error);
            FlashMessage("Some Error occurred. Check the console");
        });
    }
    else if(cut_type == 'request'){
        var path_data = {
            filesystem: from_path.filesystem,
            from_package: from_path.package,
            to_package: to_path.package,
            from_test: from_path.test_case,
            to_test: to_path.test_case,
            request: from_path.request,
        }
        $.get('request/move',path_data, function (data) {
            FlashMessage('Successfully moved');
            $.get('directory',null,function(data){
                var tree = $('#tree').fancytree('getTree');
                tree_expand.storeExpand();
                tree.reload(prepareFancyTreeData(data));
                tree.activateKey(nodepath);
                tree.getActiveNode().setExpanded(true);
                tree_expand.restoreExpand();
            }, "json");
        }, "json").fail(function (error) {
            console.log(error);
            FlashMessage("Some Error occurred. Check the console");
        });
    }

}

function view_data(node){
    if(node.data.fs_data.type != 'request') return;
    var request_name = node.title
    var request_data = node.data.fs_data.req_data
    data.show_data(request_name, request_data);
}

function check_node(node) {
    var nodes = [node];
    node.visit(function (child) {
       nodes.push(child);
    });
    nodes.forEach(function (_node) {
        _node.setActive(true);
        _node.setSelected(true);
    });
    nodes.forEach(function (_node) {
        _node.setExpanded(false);
    });
}

