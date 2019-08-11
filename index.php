<!DOCTYPE html>
<HTML>
<HEAD>
<META http-equiv="Content-Type" content="text/html; charset=utf-8" />
<TITLE>サンプル</TITLE>
</HEAD>
</BODY>
 
<?php
// file name: call_python.php
    $fullPath = 'python3 crawler.py';
    exec($fullPath, $outpara);
    echo '<HTML>';
    echo '<head>';
    echo '<title>Pythonのテスト</title>';
    echo '</head>';
    echo '<body>';
    echo '<PRE>';
    echo 'テスト<br />';
    var_dump($outpara);
    echo '<PRE>';
    echo '</body>';
    echo '</HTML>';
?>
 
</BODY>
</HTML>