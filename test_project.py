import project
import linux_cmds
import pytest
import os

def test_generate_app_info():
    var_under_test = project.generate_app_info("0x02600046  0 7799   3800 -40  1323 1120 pop-os regex101: build, test, and debug regex — Mozilla Firefox")
    correct_values = linux_cmds.User_App('7799','3800','-40','1323','1120','regex101: build, test, and debug regex — Mozilla Firefox')
    
    assert var_under_test.height == correct_values.height
    assert var_under_test.width == correct_values.width
    assert var_under_test.PID == correct_values.PID
    assert var_under_test.title == correct_values.title
    assert var_under_test.x_offset == correct_values.x_offset
    assert var_under_test.y_offset == correct_values.y_offset

    var_under_test = project.generate_app_info("0x03000007 -1 91798  3840 0    1920 1080 pop-os @!1920,0;BDHF")
    correct_values = linux_cmds.User_App('91798','3840','0','1920','1080','@!1920,0;BDHF')

    assert var_under_test.height == correct_values.height
    assert var_under_test.width == correct_values.width
    assert var_under_test.PID == correct_values.PID
    assert var_under_test.title == correct_values.title
    assert var_under_test.x_offset == correct_values.x_offset
    assert var_under_test.y_offset == correct_values.y_offset

    with pytest.raises (LookupError):
        project.generate_app_info("bad pattern foo")

def test_isSessionFile():

    os.mkdir('testSessionFile')

    #! Test 1 start
    with open("testSessionFile/dummy.sup", "xt") as f:
        f.write('foo')
        f.close()
    assert project.isSessionFile("testSessionFile/") == True
    os.remove("testSessionFile/dummy.sup")
    #! Test 1 end

    #! Test 2 start
    with open("testSessionFile/dummy.txt", "xt") as f:
        f.write('foo')
        f.close()
    assert project.isSessionFile("testSessionFile/") == False
    os.remove("testSessionFile/dummy.txt")
    #! Test 2 end

    #! Test 3 start
    with open("testSessionFile/dummy.suppppp", "xt") as f:
        f.write('foo')
        f.close()
    assert project.isSessionFile("testSessionFile/") == False
    os.remove("testSessionFile/dummy.suppppp")
    #! Test 3 end
    os.rmdir('testSessionFile')

def test_remove_app_from_list():
    app_list_under_test = []

    app = project.User_App('64849','10','114','1374','1011','apps_info_temp.txt - LoadAS - Visual Studio Code')
    app_list_under_test.append(app)
    app2 = linux_cmds.User_App('10683','5728','-20','992','1100','New Tab - Google Chrome')
    app_list_under_test.append(app2)

    app_list_under_test = project.remove_app_from_list(app_list_under_test,['chrome'])

    assert app_list_under_test[0].height == app.height
    assert app_list_under_test[0].width == app.width
    assert app_list_under_test[0].PID == app.PID
    assert app_list_under_test[0].title == app.title
    assert app_list_under_test[0].x_offset == app.x_offset
    assert app_list_under_test[0].y_offset == app.y_offset

def test_adjust_file_name_and_path():
    #! test creating a direcotry and file string
    out = project.adjust_file_name_and_path('sessions_test/session.sup')

    assert os.path.isdir('sessions_test')
    assert out == ('sessions_test/session.sup',1)

    with open(out[0],'w') as f:
        f.write('test_0')

    #! Test creating a file with +1
    out = project.adjust_file_name_and_path('sessions_test/session.sup')

    assert os.path.isdir('sessions_test')
    assert out == ('sessions_test/session1.sup',1)

    with open(out[0],'w') as f:
        f.write('test_1')

    #! Test creating a file with +2
    out = project.adjust_file_name_and_path('sessions_test/session.sup')

    assert os.path.isdir('sessions_test')
    assert out == ('sessions_test/session2.sup',2)

    with open(out[0],'w') as f:
        f.write('test_2')

    #! Test override feature
    out = project.adjust_file_name_and_path('sessions_test/session.sup',True)
    
    assert os.path.isdir('sessions_test')
    assert out == ('sessions_test/session.sup',0)

    with open(out[0],'w') as f:
        f.write('test_ovveride')

    with open('sessions_test/session.sup','r') as f:
        assert f.readline != 'test_0'

    os.remove('sessions_test/session.sup')
    os.remove('sessions_test/session1.sup')
    os.remove('sessions_test/session2.sup')
    os.rmdir('sessions_test')

def test_filename_with_default_dir():

    assert project.filename_with_default_dir("test/session.sup") == 'test/session.sup'
    assert project.filename_with_default_dir("a/b") == 'a/b'

    #! No default dir created error
    with pytest.raises (LookupError):
        project.generate_app_info("custom_session.sup")

    #! default dir created but not file error
    os.mkdir(project.DEFAULT_FILE_STORAGE)
    with pytest.raises (LookupError):
        project.generate_app_info("custom_session.sup")
    
    #! no errors and returns the full path to default location.
    with open(project.DEFAULT_FILE_STORAGE + "custom_session.sup",'w') as f:
        f.write('foo')
    
    assert project.filename_with_default_dir("custom_session.sup") == f"{project.DEFAULT_FILE_STORAGE}custom_session.sup"


