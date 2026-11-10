# Evidence and official references

Moyu source was inspected at revision `d1aa257523e929a6136937cb18aded4548d450a9`. Source inspection is not a new execution of its historical release checks.

- [Moyu project](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/src/Moyu/Moyu.csproj): target frameworks, resources, versions, PathMap.
- [Moyu packaging](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/tools/package.py): version checks, staging, private markers, archive inspection.
- [Moyu contribution guide](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/docs/contributing.md): build locks, runtime launch configuration, host verification.
- [Moyu installation guide](https://github.com/ChenmingHe0126/moyu/blob/d1aa257523e929a6136937cb18aded4548d450a9/packaging/INSTALL.md): declared Windows support and restart behavior.

Official primary references checked on 2026-11-10:

- [Moving to .NET Core](https://developer.rhino3d.com/guides/rhinocommon/moving-to-dotnet-core/)
- [Creating a Grasshopper package](https://developer.rhino3d.com/guides/yak/creating-a-grasshopper-plugin-package/)
- [Package manifest](https://developer.rhino3d.com/guides/yak/the-package-manifest/)
- [Yak CLI](https://developer.rhino3d.com/guides/yak/yak-cli-reference/)
- [Publishing a package](https://developer.rhino3d.com/guides/yak/pushing-a-package-to-the-server/)

Runtime versions and server behavior can change. Recheck the primary source before choosing a new target or promising package compatibility.
