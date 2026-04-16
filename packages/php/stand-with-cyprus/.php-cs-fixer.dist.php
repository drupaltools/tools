<?php

declare(strict_types=1);

$finder = PhpCsFixer\Finder::create()
    ->in([
        __DIR__.'/src',
    ])
;

$config = new PhpCsFixer\Config();

return $config
    ->setRiskyAllowed(true)
    ->setRules([
        '@PhpCsFixer' => true,
        '@PhpCsFixer:risky' => true,
        '@PHP74Migration' => true,
        '@PSR12' => true,
        '@PSR12:risky' => true,
    ])
    ->setFinder($finder)
;
