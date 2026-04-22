# srpc - Search and Replace while Preserving Case

```sh
$ echo "fOo FoO" > test.txt
$ srpc foo bar test.txt
$ cat test.txt
bAr BaR
```

No dependencies, just standard library modules.
Copy the script somewhere and make it executable, good to go.

Wrote this simply because I did not find any easy way to do this for a bunch of files.
