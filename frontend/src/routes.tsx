import { Icon } from './lib/chakra';
import {
  MdAutoAwesome,
} from 'react-icons/md';

// Auth Imports
import { IRoute } from './types/navigation';

const routes: IRoute[] = [
  {
    name: 'LOKA chat',
    path: '/',
    icon: (
      <Icon as={MdAutoAwesome} width="20px" height="20px" color="inherit" />
    ),
    collapse: false,
  }
];

export default routes;
