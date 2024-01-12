def nl(n=1):
    return "\n"*n


def nl_html(n=1):
    return "<br>"*n


introduction_1 = (f"<font color='orange'><b>AUFGABE 1<b></font>"
                  f"{nl_html(2)}"
                  f"Kommen wir nun zu Deiner ersten Aufgabe. Hier geht es darum die <font color='orange'>Kategorie einer Webseite zu "
                  f"identifizieren.</font>"
                  f"{nl_html(2)}"
                  f"Nutze die <font color='orange'>Taste 'n'</font> um fortzufahrern und weitere Instruktionen für die erste Webseite in "
                  f"Aufgabe 1 zu erhalten.")

introduction_2 = (f"<font color='orange'><b>AUFGABE 2<b></font>"
                  f"{nl_html(2)}"
                  f"Super! Du hast nun die Erste von 3 Aufgaben beendet."
                  f"{nl_html(2)}"
                  f"Kommen wir nun zu Deiner zweiten Aufgabe. Hier geht es darum die <font color='orange'>Funktionalität einer Webseite zu "
                  f"identifizieren</font>. Die Funktionalität einer Webseite beschreibt, was Du als Nutzer "
                  f"auf dieser Seite tun kannst."
                  f"{nl_html(2)}"
                  f"Nutze die <font color='orange'>Taste 'n'</font> um fortzufahrern und weitere Instruktionen für die erste Webseite in "
                  f"Aufgabe 2 zu erhalten.")

introduction_3 = (f"<font color='orange'><b>AUFGABE 3<b></font>"
                  f"{nl_html(2)}"
                  f"Super! Du hast nun die Zweite von 3 Aufgaben beendet."
                  f"{nl_html(2)}"
                  f"Kommen wir nun zu Deiner dritten und letzten Aufgabe. "
                  f"Hier wirst Du für jedes Bild eine neue Navigationsaufgabe bekommen. "
                  f"Die Navigationsaufgabe beschreibt das zu erreichende Ziel. "
                  f"Deine Aufgabe ist es ein <font color='orange'>Element auf der Webseite mit Deinem Blick zu "
                  f"identifizieren, mit dem Du das Ziel der Navigationsaufgabe erreichen kannst</font>."
                  f"{nl_html(2)}"
                  f"Nutze die <font color='orange'>Taste 'n'</font> um fortzufahrern und weitere Instruktionen für die erste Webseite in "
                  f"Aufgabe 3 zu erhalten.")

instruction_1 = (
    f"Sobald Du fortfährst wird es Deine Aufgabe sein die präsentierte "
    f"Webseite so lange mit Deinem Blick zu erkunden, bis Du denkst die korrekte <font color='orange'>Kategorie</font> der "
    f"Webseite identifiziert zu haben."
    f"{nl_html(2)}"
    f"Die Webseite wird einer der folgenden Kategorien zuzuordnen sein:"
    '<html>'
    '<body>'
    '<table style="text-align:center; width: 100%;">'
    '<tr>'
    '<td style="width: 50%;">'
    '<table style="width: 100%;">'
    '<tr>'
    '<td style="width: 20%;"><span style="list-style-type: square;">&bull;</span></td>'
    '<td style="width: 80%; text-align: left;"><span style="color: orange;">Community</span></td>'
    '</tr>'
    '</table>'
    '</td>'
    '<td style="width: 50%; padding-left: 20px;">'
    '<table style="width: 100%;">'
    '<tr>'
    '<td style="width: 20%;"><span style="list-style-type: circle;">&bull;</span></td>'
    '<td style="width: 80%; text-align: left;"><span style="color: orange;">E-Commerce</span></td>'
    '</tr>'
    '</table>'
    '</td>'
    '</tr>'
    '<tr>'
    '<td>'
    '<table style="width: 100%;">'
    '<tr>'
    '<td style="width: 20%;"><span style="list-style-type: square;">&bull;</span></td>'
    '<td style="width: 80%; text-align: left;"><span style="color: orange;">Entertainment</span></td>'
    '</tr>'
    '</table>'
    '</td>'
    '<td style="padding-left: 20px;">'
    '<table style="width: 100%;">'
    '<tr>'
    '<td style="width: 20%;"><span style="list-style-type: circle;">&bull;</span></td>'
    '<td style="width: 80%; text-align: left;"><span style="color: orange;">Informational</span></td>'
    '</tr>'
    '</table>'
    '</td>'
    '</tr>'
    '</table>'
    '</body>'
    '</html>'
    f"Sobald Du mit der Erkundung des Bildes fertig bist und mit der Taste 'n' fortfährst, wirst Du eine "
    f"Kategorie auswählen können. Es ist außerdem möglich, verschiedenen Bildern die gleiche "
    f"Kategorie zuzuordnen."
    f"{nl_html(2)}"
    f"Sobald Du bereit bist die Kategorie der folgenden Webseite mit Deinem Blick zu identifizieren, drücke bitte auch "
    f"jetzt schon die <font color='orange'>Taste 'n'</font> um fortzufahren."
)

instruction_2 = (
    f"Sobald Du fortfährst wird es Deine Aufgabe sein die präsentierte "
    f"Webseite so lange mit Deinem Blick zu erkunden, bis Du denkst die korrekte <font color='orange'>Funktionalität</font> der "
    f"Webseite identifiziert zu haben."
    f"{nl_html(2)}"
    f"Die Webseite wird einer der folgenden Funktionalitäten zuzuordnen sein:"
    '<html>'
    '<body>'
    '<table style="text-align:center; width: 100%;">'
    '<tr>'
    '<td style="width: 50%;">'
    '<table style="width: 100%;">'
    '<tr>'
    '<td style="width: 20%;"><span style="list-style-type: square;">&bull;</span></td>'
    '<td style="width: 80%; text-align: left;"><span style="color: orange;">Kontaktformular</span></td>'
    '</tr>'
    '<tr>'
    '<td style="width: 20%;"><span style="list-style-type: square;">&bull;</span></td>'
    '<td style="width: 80%; text-align: left;"><span style="color: orange;">Lesen von Informationen</span></td>'
    '</tr>'
    '<tr>'
    '<td style="width: 20%;"><span style="list-style-type: square;">&bull;</span></td>'
    '<td style="width: 80%; text-align: left;"><span style="color: orange;">Zahlungsabwicklung</span></td>'
    '</tr>'
    '<tr>'
    '<td style="width: 20%;"><span style="list-style-type: square;">&bull;</span></td>'
    '<td style="width: 80%; text-align: left;"><span style="color: orange;">Registrierung</span></td>'
    '</tr>'
    '</table>'
    '</td>'
    '<td style="width: 50%; padding-left: 20px;">'
    '<table style="width: 100%;">'
    '<tr>'
    '<td style="width: 20%;"><span style="list-style-type: circle;">&bull;</span></td>'
    '<td style="width: 80%; text-align: left;"><span style="color: orange;">Herunterladbare Inhalte</span></td>'
    '</tr>'
    '<tr>'
    '<td style="width: 20%;"><span style="list-style-type: circle;">&bull;</span></td>'
    '<td style="width: 80%; text-align: left;"><span style="color: orange;">Login</span></td>'
    '</tr>'
    '<tr>'
    '<td style="width: 20%;"><span style="list-style-type: circle;">&bull;</span></td>'
    '<td style="width: 80%; text-align: left;"><span style="color: orange;">Posten von Inhalten</span></td>'
    '</tr>'
    '<tr>'
    '<td style="width: 20%;"><span style="list-style-type: circle;">&bull;</span></td>'
    '<td style="width: 80%; text-align: left;"><span style="color: orange;">Visueller Medienkonsum</span></td>'
    '</tr>'
    '</table>'
    '</td>'
    '</tr>'
    '</table>'
    '</body>'
    '</html>'
    f"Sobald Du mit der Erkundung des Bildes fertig bist und mit der Taste 'n' fortfährst, wirst Du eine "
    f"Funktionalität auswählen können. Es ist außerdem möglich, verschiedenen Bildern die gleiche "
    f"Funktionalität zuzuordnen."
    f"{nl_html(2)}"
    f"Sobald Du bereit bist die Funktionalität der folgenden Webseite mit Deinem Blick zu identifizieren, drücke bitte auch "
    f"jetzt schon die <font color='orange'>Taste 'n'</font> um fortzufahren."
)

instruction_3 = (f"Sobald Du fortfährst wird es Deine Aufgabe sein die präsentierte "
                 f"Webseite so lange mit Deinem Blick zu erkunden, bis Du denkst ein <font color='orange'>Element mit Deinem Blick identifiziert zu haben, "
                 f"welches die Navigationsaufgabe löst.</font>"
                 f"{nl_html(2)}"
                 f"Sobald Du mit der Erkundung des Bildes fertig bist und mit der Taste 'n' fortfährst, wird die "
                 f"Navigationsaufgabe aufgelöst. Dort wirst Du entscheiden können, ob Du eines der "
                 f"hervorgehobenen Elemente richtig identifizieren konntest."
                 f"{nl_html(2)}"
                 f"Sobald Du die <font color='orange'>Navigationsaufgabe gelesen</font> hast und bereit bist ein Element der folgenden Webseite zu identifizieren, drücke bitte auch jetzt "
                 f"schon die <font color='orange'>Taste 'n'</font> auf der Tastatur um fortzufahren.")

instruction_final_state = (f"Das wars!"
                           f"{nl_html(2)}"
                           f"Bitte <font color='orange'>informiere nun den Versuchsleiter</font>, dass Du mit dem Experiment fertig bist."
                           f"{nl_html(2)}"
                           f"Vielen Dank, dass Du an der Eye-Tracking Studie teilgenommen hast.")

validation_result_instruction = (f"Das Ergebnis der Validierung ist minderwertig. Bitte informiere den Versuchsleiter."
                                f"{nl_html(2)}"
                                f"[AAR]"
                                 f"{nl_html(1)}"
                                 f"[AAL]"
                                 f"{nl_html(1)}"
                                 f"[APR]"
                                 f"{nl_html(1)}"
                                 f"[APL]"
                                 f"{nl_html(1)}"
                                 f"[APRR]"
                                 f"{nl_html(1)}"
                                 f"[APRL]")

statement_1 = (f"Die Erkundung der Webseite ist nun abgeschlossen. Bitte wähle nun die Kategorie aus, die "
                 f"Deiner Meinung nach diese Webseite am besten beschreibt."
                 f"{nl_html(2)}"
                 f"Bitte lass uns auch wissen, ob Du diese Webseite bereits besucht hast."
                 f"{nl_html(2)}"
                 f"Sobald Du mit Deiner Auswahl fertig bist, drücke bitte auf die Taste 'n' um mit der nächsten "
                 f"Instruktion fortzufahren.")

statement_2 = (f"Die Erkundung dieser Webseite ist nun abgeschlossen. Bitte wähle nun die Funktionalität aus, die "
                 f"Deiner Meinung nach am besten zu dieser Webseite passt."
                 f"{nl_html(2)}"
                 f"Bitte lass uns auch wissen, ob Du diese Webseite bereits besucht hast."
                 f"{nl_html(2)}"
                 f"Sobald Du mit Deiner Auswahl fertig bist, drücke bitte auf die Taste 'n' um mit der nächsten "
                 f"Instruktion fortzufahren.")

initial_validation_instruction = (f"Vielen Dank, dass Du an der Eye-Tracking Studie teilnimmst."
                                  f"{nl_html(2)}"
                                  f"Zu diesem Zeitpunkt solltest Du bereits eine Kalibrierung des Eyetrackers mit dem "
                                  f"Versuchsleiter durchgeführt haben."
                                  f"{nl_html(2)}"
                                  f"Dieses Experiment ist in 3 Aufgabenteile gegliedert. In jedem Aufgabenteil werden Dir "
                                  f"nacheinander 4 zufällige Bilder von Webseiten gezeigt. <font color='orange'>Egal in welcher Phase</font> des Experiments Du Dich befindest, gelangst Du mit der <font color='orange'>Taste 'n' zur nächsten Phase</font>."
                                  f"{nl_html(2)}"
                                  f"Zu Beginn und zum Ende muss die <font color='orange'>Kalibrierung</font> des Eyetrackers allerdings noch <font color='orange'>validiert</font> werden um sicherzustellen, dass die Blickdaten akkurat aufgezeichnet werden."
                                  f"{nl_html(2)}"
                                  f"Für die Validierung bitten wir Dich im folgenden Fenster auf die "
                                  f"<font color='orange'>weißen Punkte zu Blicken</font>. Wenn Du bereit bist die "
                                  f"Validierung zu starten, drücke bitte auf die <font color='orange'>Taste 'n'</font>.")

final_validation_instruction = (f"Fast geschafft!"
                                f"{nl_html(2)}"
                                f"Nur noch einmal die <font color='orange'>Kalibrierung</font> des Eyetrackers <font color='orange'>validieren</font> und das Experiment ist zu Ende."
                                f"{nl_html(2)}"
                                f"Für die Validierung bitten wir Dich im folgenden Fenster erneut auf die "
                                f"<font color='orange'>weißen Punkte</font> zu Blicken. Wenn Du bereit bist die "
                                f"Validierung zu starten, drücke bitte auf die <font color='orange'>Taste 'n'</font>.")

navigationtask_1 = "Mit welchem Element würdest Du interagieren um <font color='red'>die Karriereseite zu erreichen</font>?"

navigationtask_2 = "Mit welchem Element würdest Du interagieren um <font color='red'>einen Gegenstand in den Einkaufswagen zu legen</font>?"

navigationtask_3 = "Mit welchem Element würdest Du interagieren um <font color='red'>die Startseite zu erreichen</font>?"

navigationtask_4 = "Mit welchem Element würdest Du interagieren um <font color='red'>Dich einzuloggen</font>?"

navigationtask_5 = "Mit welchem Element würdest Du interagieren um <font color='red'>Dich auszuloggen</font>?"

navigationtask_6 = "Mit welchem Element würdest Du interagieren um <font color='red'>zur Zahlungsabwicklung zu gelangen</font>?"

navigationtask_7 = "Mit welchem Element würdest Du interagieren um <font color='red'>Inhalte zu posten</font>?"

navigationtask_8 = "Mit welchem Element würdest Du interagieren um <font color='red'>Dich zu registrieren</font>?"