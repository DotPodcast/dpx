import Controller from '@ember/controller';

export default Controller.extend(
  {
    init() {
      this._super(...arguments)
      this.set('downloadsByDevice',
        [
          {
            period: '2010 Q1',
            iphone: 2666,
            ipad: null,
            itouch: 2647
          },
          {
            period: '2010 Q2',
            iphone: 2778,
            ipad: 2294,
            itouch: 2441
          },
          {
            period: '2010 Q3',
            iphone: 4912,
            ipad: 1969,
            itouch: 2501
          },
          {
            period: '2010 Q4',
            iphone: 3767,
            ipad: 3597,
            itouch: 5689
          },
          {
            period: '2011 Q1',
            iphone: 6810,
            ipad: 1914,
            itouch: 2293
          },
          {
            period: '2011 Q2',
            iphone: 5670,
            ipad: 4293,
            itouch: 1881
          },
          {
            period: '2011 Q3',
            iphone: 4820,
            ipad: 3795,
            itouch: 1588
          },
          {
            period: '2011 Q4',
            iphone: 15073,
            ipad: 5967,
            itouch: 5175
          },
          {
            period: '2012 Q1',
            iphone: 10687,
            ipad: 4460,
            itouch: 2028
          },
          {
            period: '2012 Q2',
            iphone: 8432,
            ipad: 5713,
            itouch: 1791
          }
        ]
      )

      this.set('deviceNames', ['iPhone', 'iPad', 'iPod Touch'])
      this.set('deviceKeys', ['iphone', 'ipad', 'itouch'])

      this.set('seriesFunding',
        [
          {
            y: '2006',
            a: 100,
            b: 90
          },
          {
            y: '2007',
            a: 75,
            b: 65
          },
          {
            y: '2008',
            a: 50,
            b: 40
          },
          {
            y: '2009',
            a: 75,
            b: 65
          },
          {
            y: '2010',
            a: 50,
            b: 40
          },
          {
            y: '2011',
            a: 75,
            b: 65
          },
          {
            y: '2012',
            a: 100,
            b: 90
          }
        ]
      )

      this.set('seriesKeys', ['a', 'b'])
      this.set('seriesLabels', ['Series A', 'Series B'])

      this.set('salesData',
        [
          {
            label: "Download sales",
            value: 12
          },
          {
            label: "In-Store sales",
            value: 30
          },
          {
            label: "Mail-Order sales",
            value: 20
          }
        ]
      )
    }
  }
);
