/**
 * Copyright (C) 2025 Guillaume Kulakowski <guillaume@kulakowski.fr>
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */

import * as bulmaToast from "bulma-toast";

bulmaToast.setDefaults({
  duration: 5000,
  position: "bottom-right",
  dismissible: false,
  pauseOnHover: true,
  closeOnClick: true,
  opacity: 1,
  animate: { in: "fadeIn", out: "fadeOut" },
});
