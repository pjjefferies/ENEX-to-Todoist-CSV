# import datetime as dt
from enum import Enum, auto

from box import Box
import pandas as pd

from src.strip_extension import strip_extension
from src.load_import_data import load_enex_backup
from src.config.config_main import load_config
from src.config.config_logging import logger

cfg: Box = load_config()

WHEN_TAGS: list[str] = cfg.DATABASE.TAGS.WHEN
WHERE_TAGS: list[str] = cfg.DATABASE.TAGS.WHERE


class NoteType(Enum):
    TASK = auto()
    REFERENCE_NOTE = auto()
    PROJECT = auto()
    UNKNOWN = auto()


def save_enex_backup_to_todoist_csv(
    *, enex_backup_pathname: str, todoist_csv_pathname: str
):
    # Load Data from ENEX file(s)
    notes, _ = load_enex_backup(filepath=enex_backup_pathname, logger=logger)

    header = [
        "TYPE",
        "CONTENT",
        "DESCRIPTION",
        "PRIORITY",
        "INDENT",
        "AUTHOR",
        "RESPONSIBLE",
        "DATE",
        "DATE_LANG",
        "TIMEZONE",
        "DURATION",
        "DURATION_UNIT",
    ]

    notes_df = pd.DataFrame({}, columns=header)

    for note in notes:
        note_type: NoteType = NoteType.REFERENCE_NOTE  # default
        this_note_tags: set[str] = set()
        this_tag: str
        empty_tags: list[str] = []
        for this_tag in note.get("tags", empty_tags):
            if this_tag in WHERE_TAGS or this_tag in WHEN_TAGS:
                note_type = NoteType.TASK
            this_note_tags.add("@" + this_tag)

        if "source-url" in note:
            source_url: str = note["source-url"]
        else:
            source_url = ""

        match note_type:
            case NoteType.TASK:
                new_task: "pd.Series[str]" = pd.Series(
                    {
                        "TYPE": "task",
                        "CONTENT": " ".join([note["title"]] + list(this_note_tags)),
                        "DESCRIPTION": "\t".join([source_url, note["content"]]),
                        "PRIORITY": 1,
                        "INDENT": 1,
                        "AUTHOR": "",
                        "RESPONSIBLE": "",
                        "DATE": note["updated"],
                    }
                )
                notes_df = pd.concat(
                    [notes_df, new_task.to_frame().T], axis=0, ignore_index=True
                )

            case NoteType.REFERENCE_NOTE:
                pass

            case _:
                pass

    notes_df.to_csv(
        path_or_buf=todoist_csv_pathname, columns=header, index=False, encoding="utf-8"
    )


if __name__ == "__main__":
    filename: str = "Evernote_Actions_2023-10-23 (Final).enex"
    enex_backup_pathname: str = f"data/import_data/{filename}"
    todoist_csv_pathname: str = f"data/todoist_csv/{strip_extension(filename)}.csv"

    save_enex_backup_to_todoist_csv(
        enex_backup_pathname=enex_backup_pathname,
        todoist_csv_pathname=todoist_csv_pathname,
    )
