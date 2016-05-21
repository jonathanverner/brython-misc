(function(app) {
    document.addEventListener('DOMContentLoaded', function() {
        System.import("app/tsapp.component.js").then(function (app) {
            console.log(app);
            ng.platformBrowserDynamic.bootstrap(app.AppComponent);
        })
//         System.import("primeng/primeng").then(function(primeng) {
//             console.log(primeng);
//             console.log(primeng.Menubar);
//             app.AppComponent =
//                 ng.core.Component({
//                     selector: 'my-app',
//                     template: '<h1>My First Angular 2 App</h1>',
//                     directives: [primeng.Menubar]
//                 })
//                 .Class({
//                     constructor: function() {}
//                 });
//             ng.platformBrowserDynamic.bootstrap(app.AppComponent);
//         });
    });
})(window.app || (window.app = {}));
