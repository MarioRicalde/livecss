syntax_color_template = """
                <dict>
                    <key>captures</key>
                    <dict>
                        <key>1</key>
                        <dict>
                            <key>name</key>
                            <string>punctuation.defprepare_envion.constant.css</string>
                        </dict>
                    </dict>
                    <key>match</key>
                    <string>{0}</string>
                    <key>name</key>
                    <string>{1}.css-colorize.css</string>
                </dict>
"""
template = """
        <key>facepalm-values</key>
        <dict>
            <key>patterns</key>
            <array>
                {0}
            </array>
        </dict>
"""
include = """
<dict>
    <key>include</key>
    <string>#facepalm-values</string>
</dict>
"""

theme_templ = """
    <dict>
        <key>name</key>
        <string>\'{0}\'</string>
        <key>scope</key>
        <string>{0}.css-colorize.css</string>
        <key>settings</key>
        <dict>
            <key>background</key>
            <string>{1}</string>
            <key>foreground</key>
            <string>{2}</string>
        </dict>
    </dict>
"""