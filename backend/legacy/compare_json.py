import json
import time


def json_comparison_html(json_1, json_2, title='Json Comparison'):
    json_str_1 = json.dumps(json_1)
    json_str_2 = json.dumps(json_2)

    uid = str(time.time()).replace('.', '')

    return '''
    <html>
        <head>
            <meta charset="UTF-8">
            <title>JSON Comparator</title>
            <link href="https://fonts.googleapis.com/css?family=Source+Sans+Pro:400" rel="stylesheet">
            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css">
            <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.0/jquery.min.js"></script>
            <script src="https://www.gstatic.com/charts/loader.js"></script>
            <style>
                .miss-match {
                    color: red;
                }

                #'''+uid+''' {
                    background-color: antiquewhite;
                    margin-top: 50px;
                    table-layout: fixed;
                }

                #'''+uid+''' td {
                    word-wrap: break-word;
                }

                #'''+uid+''' th {
                    text-align: center;
                }
            </style>
        </head>
        <body>
        <div class="container">
            <div class="row">
                <div class="col-md-12" row="30">
                    <table class="table" width="100%" id="'''+uid+'''">
                        <thead>
                            <tr>
                                <th colspan='2'>'''+title+'''</th>
                            </tr>
                            <tr>
                                <th width="50%">Expected</th>
                                <th width="50%">Got</th>
                            </tr>
                        </thead>
                    </table>
                </div>
            </div>
        </div>
        </body>
        <script>
            var original_data = ''' + json_str_1 + ''';
            var miss_data = ''' + json_str_2 + ''';

            function replacer(key, value){
                var ignorePatter = /.*_id|^_/;
                if(ignorePatter.test(key)){
                    return undefined;
                }
                return value;
            }
            var jsonTxt1 = JSON.stringify(original_data, replacer, 4);
            var jsonTxt2 = JSON.stringify(miss_data, replacer, 4);

            var origLines = jsonTxt1.split("\\n");
            var newLines = jsonTxt2.split("\\n");
            var fl = 0, cls, td1, td2;
            for (var i = 0; i < origLines.length; i++) {
                if (origLines[i] == newLines[i])
                    cls = 'matched';
                else
                    cls = 'miss-match';

                td1 = '<td><span class="'+cls+'">' + origLines[i].replace(/\s/g, '&nbsp;') + '</span></td>';
                td2 = '<td><span class="'+cls+'">' + newLines[i].replace(/\s/g, '&nbsp;') + '</span></td>';
                $("#'''+uid+'''").find("tr:last").after('<tr>'+td1+td2+'</tr>');
            }
        </script>
        </html>
    '''

if __name__ == '__main__':
    import webbrowser, os, sys

    # import testing JSON files to Python structures
    with open('a.json') as f:
        json_str1 = f.read()

    with open('b.json') as f:
        json_str2 = f.read()

    html = json_comparison_html(json_str1, json_str2)
    with open('output.html', 'w') as f:
        f.write(html)

    root_path = sys.path[0]
    webbrowser.open(os.path.join(root_path, 'output.html'))
