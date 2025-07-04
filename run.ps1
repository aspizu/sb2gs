param (
    [string]$command = $(throw "Command is required")
)

switch ($command) {
    "test" {
        foreach ($project in get-childitem -path tests/* -include *.sb3) {
            python -m sb2gs $project --overwrite --verify
        }
    }
    default {
        throw "Unknown command: $command"
    }
}
