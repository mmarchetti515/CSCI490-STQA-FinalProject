wifiHTMLStart = \
"""
<!doctype html>
<html lang = "en-US">
    <head>
        <meta charset = "utf-8" name = "viewport" content = "width=device-width, initial-scale = 1.0">
            <title> Configure WI-FI </title>
        </meta>
    </head>

    <header>
    <h1> Connect to Wi-Fi</h1>
    </header>
    
    <form action = "connect" method = "get">
        <label for = "ssid"> Select an access point: </label>
        <select name = "ssid"> 
"""

wifiHTMLEnd = \
"""
        </select>
        
        <br>

        <label for = "pass"> Password: </label>
        <input type = "password" name = "password">

        <br><br>
        <input type = "submit" value = "Submit">

    </form>

</html>  
"""

wifiConnectSuccessHTML = \
"""
<!doctype html>
<html lang = "en-US">
    <head>
        <meta charset = "utf-8" name = "viewport" content = "width=device-width, initial-scale = 1.0">
            <title> Configure WI-FI </title>
        </meta>
    </head>

    <header>
      <h1> Connection to {x} was successful! </h1>
    </header>

</html>
"""

wifiConnectFailedHTML = \
"""
<!doctype html>
<html lang = "en-US">
    <head>
        <meta charset = "utf-8" name = "viewport" content = "width=device-width, initial-scale = 1.0">
            <title> Configure WI-FI </title>
        </meta>
    </head>

    <header>
      <h1> Connection to {x} was not sucessfull </h1>
    </header>

    <form> <input type = "button" value = "Return" onclick = "history.back()" > </form>
</html>
"""