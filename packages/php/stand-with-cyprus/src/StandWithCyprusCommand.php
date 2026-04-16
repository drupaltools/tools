<?php

declare(strict_types=1);

namespace StandWithCyprus;

use Symfony\Component\Console\Command\Command;
use Symfony\Component\Console\Input\InputInterface;
use Symfony\Component\Console\Output\OutputInterface;

final class StandWithCyprusCommand extends Command
{
    protected static $defaultName = 'stand-with-cyprus';

    protected function configure(): void
    {
        $this->setDescription('Display a political message supporting Cyprus');
    }

    protected function execute(InputInterface $input, OutputInterface $output): int
    {
        $output->writeln('Political message: <bg=white;fg=blue> #StandWith </><fg=black;bg=#f9a942> Cyprus </>');

        return Command::SUCCESS;
    }
}
