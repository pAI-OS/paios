<%
-- Lua code to load the configuration
local config = require("config")
local abilities = config.getAbilities()
%>

<!DOCTYPE html>
<html>
<head>
    <title>Kwaai's Personal AI Operating System</title>
    <link rel="stylesheet" type="text/css" href="styles.css">
</head>
<body>
    <div id="sidebar">
        <ul>
        <% for i, ability in ipairs(abilities) do %>
            <li><a href="#<%= ability.id %>"><%= ability.name %></a></li>
        <% end %>
        </ul>
    </div>
    <div id="content">
        <% for i, ability in ipairs(abilities) do %>
            <div id="<%= ability.id %>">
                <h2><%= ability.name %></h2>
                <!-- Include the configuration options for each ability here -->
            </div>
        <% end %>
    </div>
</body>
</html>
