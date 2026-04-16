# \#StandWithCyprus

!["StandWithCyprus example"](standwithcyprus.jpeg)

## About

This is a political message for composer about the "Turkish invasion of Cyprus" which started in 1974.

See more on [Wikipedia - Turkish invasion of Cyprus](https://en.wikipedia.org/wiki/Turkish_invasion_of_Cyprus).

You can add `#StandWithCyprus` to the console of your php project.

## Installation

This package contains only a [single Command Application](https://symfony.com/doc/current/components/console/single_command_tool.html).

Add the composer require command from the Terminal:

```bash
composer require tplcom/stand-with-cyprus
```

Add an entry on the composer.json `scripts` 'post-install-cmd' or any other hook:

```composer
scripts: {
  "post-install-cmd": [
    "stand-with-cyprus"
  ]
}
```

## Development

- We create the binary using [box](https://github.com/box-project/box).

```bash
git clone git@github.com:theodorosploumis/stand-with-cyprus.git
cd stand-with-cyprus
composer install

composer build
```
