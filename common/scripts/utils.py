import pyscreenshot


def get_error_case(cases_path):
    with open(cases_path) as file:
        cases = json.load(file)

    for case in cases:
        if case["status"] == "progress":
            case["status"] = "error"

            with open(cases_path, "w") as file:
                json.dump(cases, file, indent=4)

            return case["case"]
    else:
        return False


def make_error_screen(cases_path, case, screen_path):
    screen = pyscreenshot.grab()
    screen.save(screen_path)

    with open(cases_path) as file:
        cases = json.load(file)

    cases[case]['error_screen_path'] = screen_path

    with open(cases_path, "w") as file:
        json.dump(cases, file, indent=4)
