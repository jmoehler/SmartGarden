# Statuscodes

| Code  |Bedeutung| Aktion                              |
|-------|---------|-------------------------------------|
| `101` | EC-value went from 'too low' to 'just right' | - |
| `102` | EC-value went from 'too low' to 'too high' | add water |
| `103` | EC-value went from 'just right' to 'too low' | add fertilizer |
| `104` | EC-value went from 'just right' to 'too high' | add water |
| `105` | EC-value went from 'too high' to 'just right' | - |
| `106` | EC-value went from 'too high' to 'too low' | add fertilizer |
| `107` | EC-value is 'too low', even after multiple attempts to fix it | log critical event |
| `108` | EC-value is 'too high', even after multiple attempts to fix it | log critical event |
| `201` | pH-value went from 'too low' to 'just right' | - |
| `202` | pH-value went from 'too low' to 'too high' | add citric acid |
| `203` | pH-value went from 'just right' to 'too low' | add soda water |
| `204` | pH-value went from 'just right' to 'too high' | add citric acid |
| `205` | pH-value went from 'too high' to 'just right' | - |
| `206` | pH-value went from 'too high' to 'too low' | add soda water |
| `207` | pH-value is 'too low', even after multiple attempts to fix it | log critical event |
| `208` | pH-value is 'too high', even after multiple attempts to fix it | log critical event |
| `307` | Water level is 'too low', even after multiple attempts to fix it | log critical event |

