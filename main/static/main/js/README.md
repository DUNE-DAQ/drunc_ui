# JS dependencies

These JS dependencies are bundled here for convenience and for some of the reasons
outlined in [this blog post](https://blog.wesleyac.com/posts/why-not-javascript-cdn),
but they should be checked from time to time and update them when need it.

The currently downloaded versions of the libraries are:

- Hyperscript:
    - **web**: <https://hyperscript.org/>
    - **current version**: 0.9.14
    - **download link**:
        - <https://unpkg.com/hyperscript.org@X.Y.Z/dist/_hyperscript.min.js>
- HTMX:
    - **web**: <https://htmx.org/>
    - **current version**: 2.0.4
    - **download link**:
        - <https://unpkg.com/htmx.org@X.Y.Z/dist/htmx.min.js>
- Boostrap:
    - **web**: <https://getbootstrap.com/>
    - **current version**: 5.3.6
    - **download link**:
        - <https://cdn.jsdelivr.net/npm/bootstrap@X.Y.Z/dist/css/bootstrap.min.css>
        - <https://cdn.jsdelivr.net/npm/bootstrap@X.Y.Z/dist/js/bootstrap.bundle.min.js>
- Bootswatch (boostrap theme) - Sandstone:
    - **web**: <https://bootswatch.com>
    - **current version**: 5.3.6
    - **download link**: Download the CSS file from the top menu.
        - <https://bootswatch.com/sandstone/>

## Update process

The general process to update these dependencies is:

- Find their latest version in the tool webpage.
- Us the download link provided replacing `X.Y.Z` with the actual version number found.
- Update the correspoinding file with the new data.
- **Update this README with the new versions**.

For some dependencies like bootstrap, this should be done for both the `js` code and the
`css` code. If a theme is used for Bootstrap, that should be downloaded separately and
replace the default bootstrap `css` file. Version numbers of the theme and Bootstrap
**must match**.
