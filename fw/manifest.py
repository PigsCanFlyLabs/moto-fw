include("$(BOARD_DIR)/../manifest.py")


freeze(".",
       ("boot.py",
        "LSM6DS3TR.py",
        "test_utils.py",
       ),
)
