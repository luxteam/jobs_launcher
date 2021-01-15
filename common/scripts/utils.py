import json
import pyscreenshot


def get_error_case(cases_path):
    with open(cases_path) as file:
        cases = json.load(file)

    for case in cases:
        if case["status"] == "inprogress":
            case["status"] = "error"

            with open(cases_path, "w") as file:
                json.dump(cases, file, indent=4)

            return case["case"]
    else:
        return False


def make_error_screen(case_path, absolute_screen_path, relative_screen_path):
    screen = pyscreenshot.grab()
    screen.save(absolute_screen_path)

    with open(case_path) as file:
        case_json = json.load(file)[0]

    case_json["error_screen_path"] = relative_screen_path

    with open(case_path, "w") as file:
        json.dump([case_json], file, indent=4)
